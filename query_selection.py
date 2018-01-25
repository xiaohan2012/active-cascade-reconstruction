import random
import numpy as np
from tqdm import tqdm
from core import uncertainty_scores
from graph_tool.centrality import pagerank
from graph_helpers import extract_nodes, k_hop_neighbors


class NoMoreQuery(Exception):
    pass


class BaseQueryGenerator():
    def __init__(self, g, obs=None, c=None):
        self.g = g
        if obs is not None:
            self.receive_observation(obs, c)
        else:
            self._cand_pool = None

    def receive_observation(self, obs, c):
        self._cand_pool = set(extract_nodes(self.g)) - set(obs)

    def select_query(self, *args, **kwargs):
        if len(self._cand_pool) == 0:
            raise NoMoreQuery()
        
        q = self._select_query(*args, **kwargs)
        self._cand_pool.remove(q)
        return q

    def _select_query(self, *args, **kwargs):
        raise NotImplementedError('do it yourself!')

    def update_pool(self, g):
        """some nodes might be removed from g, thus they are not selectble from self._cand_pool
        """
        visible_nodes = set(extract_nodes(g))
        self._cand_pool = list(set(self._cand_pool).intersection(visible_nodes))

    def empty(self):
        return len(self._cand_pool) == 0


class RandomQueryGenerator(BaseQueryGenerator):
    """random query generator"""

    def _select_query(self, *args, **kwargs):
        return random.choice(list(self._cand_pool))


class PRQueryGenerator(BaseQueryGenerator):
    """rank node by pagerank score
    """
    def receive_observation(self, obs, c):
        # personalized vector for pagerank
        # print('START: pagerank')
        pers = self.g.new_vertex_property('float')
        for o in obs:
            pers[o] = 1 / len(obs)
        rank = pagerank(self.g, pers=pers)

        self.pr = {}
        for v in self.g.vertices():
            self.pr[int(v)] = rank[v]
        # print('DONE: pagerank')
        super(PRQueryGenerator, self).receive_observation(obs, c)

    def _select_query(self, *args, **kwargs):
        return max(self._cand_pool, key=self.pr.__getitem__)


class SamplingBasedGenerator(BaseQueryGenerator):
    def __init__(self, g, sampler, root_sampler=None, *args, **kwargs):
        self.sampler = sampler
        assert root_sampler in {None, 'earliest_obs', 'earliest_nbrs'}
        self.root_sampler = root_sampler
        super(SamplingBasedGenerator, self).__init__(g, *args, **kwargs)

    def _earlier_root_sampler(self, obs, c):
        def f():
            return min(obs, key=lambda o: c[o])
        return f

    def _early_nbrs_sampler(self, obs, c, k=1):
        earliest_node = min(obs, key=lambda o: c[o])
        nbrs = list(k_hop_neighbors(earliest_node, self.g, k=k)) + [earliest_node]

        def f():
            return random.choice(nbrs)
        return f
    
    def receive_observation(self, obs, c):
        # print('START: sampler.fill')
        if self.root_sampler == 'earliest_obs':
            root_sampler = self._earlier_root_sampler(obs, c)
        elif self.root_sampler == 'earliest_nbrs':
            root_sampler = self._early_nbrs_sampler(obs, c)
        else:
            root_sampler = self.root_sampler
            
        self.sampler.fill(obs,
                          root_sampler=root_sampler)
        # print('DONE: sampler.fill')
        super(SamplingBasedGenerator, self).receive_observation(obs, c)

    def update_samples(self, g, inf_nodes, node, label):
        """update the tree samples"""
        new_samples = self.sampler.update_samples(inf_nodes, node, label)
        return new_samples


class EntropyQueryGenerator(SamplingBasedGenerator):
    def __init__(self, g, *args, method='entropy', **kwargs):
        self.method = method

        super(EntropyQueryGenerator, self).__init__(g, *args, **kwargs)

    def _select_query(self, g, inf_nodes):
        # need to resample the spanning trees
        # because in theory, uninfected nodes can be removed from the graph
        scores = uncertainty_scores(
            g, inf_nodes,
            self.sampler,
            method=self.method)
        q = max(self._cand_pool, key=scores.__getitem__)
        return q


class PredictionErrorQueryGenerator(SamplingBasedGenerator):
    """OUR CONTRIBUTION"""
    def __init__(self, *args,
                 error_estimator,
                 prune_nodes=False,
                 n_node_samples=None, **kwargs):
        """
        n_node_samples: number of nodes used to estimate probabilities
        pass None if using all of them.
        """
        self.error_estimator = error_estimator
        self.min_proba = kwargs.get('min_proba', 0.0)
        self.n_node_samples = n_node_samples
        self.prune_nodes = prune_nodes

        super(PredictionErrorQueryGenerator, self).__init__(*args, **kwargs)

    def receive_observation(self, obs, c):
        super(PredictionErrorQueryGenerator, self).receive_observation(obs, c)
        # add samples to error estimator
        self.error_estimator.build_matrix(self.sampler.samples)

    def update_samples(self, g, inf_nodes, node, label):
        new_samples = super(PredictionErrorQueryGenerator, self).update_samples(g, inf_nodes, node, label)

        # remember this
        self.error_estimator.update_trees(new_samples, node, label)

    # @profile
    def _select_query(self, g, inf_nodes):
        if self.prune_nodes:
            # pruning nods that are sure to be infected/uninfected
            # also, we can set a real-valued threshold
            self._cand_pool = set(
                self.error_estimator.filter_out_extreme_targets(
                    self._cand_pool,
                    min_value=self.min_proba))

        if ((self.n_node_samples is None) or self.n_node_samples >= len(self._cand_pool)):
            node_samples = self._cand_pool
        else:
            # use node samples to estimate prediction error
            cand_node_samples = list(self._cand_pool)
            node_sample_inf_proba = self.error_estimator.unconditional_proba(cand_node_samples)
            # node_sample_inf_proba = np.array(
            #     [len(matching_trees(self.sampler.samples, n, 1)) / len(self.sampler.samples)
            #      for n in cand_node_samples])

            # the closer to 0.5, the better
            val1 = node_sample_inf_proba * 2
            val2 = (1 - node_sample_inf_proba) * 2
            sampling_weight = np.where(val1 < val2, val1, val2)  # take the pairwise minimum
            assert (sampling_weight <= 1).all()

            sampling_weight /= sampling_weight.sum()

            node_samples = np.random.choice(cand_node_samples, self.n_node_samples,
                                            p=sampling_weight)

        def score(q):
            return self.error_estimator.query_score(q, set(node_samples) - {q})

        if False:
            e = {q: score(q) for q in tqdm(self._cand_pool)}
        else:
            q2score = {}
            # for q in tqdm(self._cand_pool)
            for q in self._cand_pool:
                q2score[q] = score(q)

            # import pickle as pkl
            # import tempfile
            # with tempfile.NamedTemporaryFile(dir='./tmp', delete=False) as f:
            #     pkl.dump(q2score, f)
            #     f.flush()
            
        # top = 10
        # top_qs = list(sorted(q2score, key=q2score.__getitem__))[:top]

        # print('top score queries:')
        # for q in top_qs:
        #     print('{}({:.2f})'.format(q, q2score[q]))

        # changed to max
        best_q = max(self._cand_pool, key=q2score.__getitem__)
        # best_q = min(self._cand_pool, key=q2score.__getitem__)
        # print('best_q', best_q)
        return best_q
