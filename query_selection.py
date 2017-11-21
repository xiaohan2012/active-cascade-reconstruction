import random
import numpy as np
from core import uncertainty_scores, sample_steiner_trees
from core1 import query_score, matching_trees
from graph_tool.centrality import pagerank
from graph_helpers import extract_nodes


class BaseQueryGenerator():
    def __init__(self, g, obs=None):
        self.g = g
        if obs is not None:
            self.receive_observation(obs)
        else:
            self._pool = None
        
    def receive_observation(self, obs):
        self._pool = set(extract_nodes(self.g)) - set(obs)

    def select_query(self, *args, **kwargs):
        assert self._pool, 'no more node to query'
        q = self._select_query(*args, **kwargs)
        self._pool.remove(q)
        return q

    def _select_query(self, *args, **kwargs):
        raise NotImplementedError('do it yourself!')

    def update_pool(self, g):
        """some nodes might be removed from g, thus they are not selectble from self._pool
        """
        visible_nodes = set(extract_nodes(g))
        self._pool = list(set(self._pool).intersection(visible_nodes))
        
    def empty(self):
        return len(self._pool) == 0


class RandomQueryGenerator(BaseQueryGenerator):
    """random query generator"""

    def _select_query(self, *args, **kwargs):
        return random.choice(list(self._pool))


class EntropyQueryGenerator(BaseQueryGenerator):
    """OUR CONTRIBUTION"""
    def __init__(self, *args, num_stt=25, method='entropy', use_resample=False):
        self.num_stt = num_stt
        self.method = method
        self.use_resample = use_resample

        super(EntropyQueryGenerator, self).__init__(*args)

    def _select_query(self, g, inf_nodes):
        # need to resample the spanning trees
        # because in theory, uninfected nodes can be removed from the graph
        self.steiner_tree_samples = sample_steiner_trees(
            self.g, inf_nodes,
            n_samples=self.num_stt)
        
        scores = uncertainty_scores(
            g, inf_nodes,
            num_stt=self.num_stt,
            method=self.method,
            use_resample=self.use_resample,
            steiner_tree_samples=self.steiner_tree_samples)
        q = max(self._pool, key=scores.__getitem__)
        return q


class PRQueryGenerator(BaseQueryGenerator):
    """rank node by pagerank score
    """
    def receive_observation(self, obs):
        # personalized vector for pagerank
        pers = self.g.new_vertex_property('float')
        for o in obs:
            pers[o] = 1 / len(obs)
        rank = pagerank(self.g, pers=pers)

        self.pr = {}
        for v in self.g.vertices():
            self.pr[int(v)] = rank[v]

        super(PRQueryGenerator, self).receive_observation(obs)
        
    def _select_query(self, *args, **kwargs):
        return max(self._pool, key=self.pr.__getitem__)


class PredictionErrorQueryGenerator(BaseQueryGenerator):
    """OUR CONTRIBUTION"""
    def __init__(self, *args, num_stt=25, n_node_samples=None):
        self.num_stt = num_stt
        self.n_node_samples = n_node_samples
        super(PredictionErrorQueryGenerator, self).__init__(*args)

    def _select_query(self, g, inf_nodes):
        steiner_tree_samples = sample_steiner_trees(
            self.g, inf_nodes,
            n_samples=self.num_stt)

        T = [set(extract_nodes(t)) for t in steiner_tree_samples]  # node set

        # pruning nods that are sure to be infected/uninfected
        self._pool = {i for i in self._pool
                      if len(matching_trees(T, i, 0)) / len(T) not in {0, 1}}
        
        if ((self.n_node_samples is None) or self.n_node_samples >= len(self._pool)):
            node_samples = self._pool
        else:
            cand_node_samples = list(self._pool)
            node_sample_inf_proba = np.array([len(matching_trees(T, n, 1)) / len(T)
                                              for n in cand_node_samples])

            # the closer to 0.5, the better
            val1 = node_sample_inf_proba * 2
            val2 = (1 - node_sample_inf_proba) * 2
            sampling_weight = np.where(val1 < val2, val1, val2)  # take the pairwise minimum
            assert (sampling_weight <= 1).all()
                                 
            sampling_weight /= sampling_weight.sum()

            node_samples = np.random.choice(cand_node_samples, self.n_node_samples,
                                            p=sampling_weight)

        def score(q):
            s = query_score(q, T,
                            set(node_samples) - {q})
            return s
        from tqdm import tqdm
        q2score = {q: score(q) for q in tqdm(self._pool)}
        # top = 10
        # top_qs = list(sorted(q2score, key=q2score.__getitem__))[:top]

        # print('top score queries:')
        # for q in top_qs:
        #     print('{}({:.2f})'.format(q, q2score[q]))
            
        best_q = min(self._pool, key=q2score.__getitem__)
        # print('best_q', best_q)
        return best_q
