import random
import numpy as np
from core import uncertainty_scores
from core1 import query_score, matching_trees
from graph_tool.centrality import pagerank
from graph_helpers import extract_nodes


class BaseQueryGenerator():
    def __init__(self, g, obs=None):
        self.g = g
        if obs is not None:
            self.receive_observation(obs)
        else:
            self._cand_pool = None
        
    def receive_observation(self, obs):
        self._cand_pool = set(extract_nodes(self.g)) - set(obs)

    def select_query(self, *args, **kwargs):
        assert self._cand_pool, 'no more node to query'
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
        return max(self._cand_pool, key=self.pr.__getitem__)


class SamplingBasedGenerator(BaseQueryGenerator):
    def __init__(self, g, tree_pool, *args, **kwargs):
        self.tree_pool = tree_pool
        super(SamplingBasedGenerator, self).__init__(g, *args, **kwargs)

    def receive_observation(self, obs):
        self.tree_pool.fill(obs)
        super(SamplingBasedGenerator, self).receive_observation(obs)

    def update_samples(self, g, inf_nodes, node, label):
        """update the tree samples"""
        self.tree_pool.update_samples(inf_nodes, node, label)

    
class EntropyQueryGenerator(SamplingBasedGenerator):
    def __init__(self, g, *args, method='entropy', use_resample=False, **kwargs):
        self.method = method
        self.use_resample = use_resample

        super(EntropyQueryGenerator, self).__init__(g, *args, **kwargs)
        
    def _select_query(self, g, inf_nodes):
        # need to resample the spanning trees
        # because in theory, uninfected nodes can be removed from the graph
        scores = uncertainty_scores(
            g, inf_nodes,
            method=self.method,
            use_resample=self.use_resample,
            steiner_tree_samples=self.tree_pool.tree_samples)
        q = max(self._cand_pool, key=scores.__getitem__)
        return q


class PredictionErrorQueryGenerator(SamplingBasedGenerator):
    """OUR CONTRIBUTION"""
    def __init__(self, *args,
                 prune_nodes=False,
                 n_node_samples=None, **kwargs):
        """
        n_node_samples: number of nodes used to estimate probabilities
        pass None if using all of them.
        """
        self.n_node_samples = n_node_samples
        self.prune_nodes = prune_nodes
        
        super(PredictionErrorQueryGenerator, self).__init__(*args, **kwargs)
        
    def _select_query(self, g, inf_nodes):
        if self.prune_nodes:
            # pruning nods that are sure to be infected/uninfected
            # also, we can set a real-valued threshold
            self._cand_pool = {
                i for i in self._cand_pool
                if len(matching_trees(self.tree_pool.nodes_samples, i, 0)) / self.tree_pool.n_samples
                not in {0, 1}}
        
        if ((self.n_node_samples is None) or self.n_node_samples >= len(self._cand_pool)):
            node_samples = self._cand_pool
        else:
            # use node samples to estimate prediction error
            cand_node_samples = list(self._cand_pool)
            node_sample_inf_proba = np.array(
                [len(matching_trees(self.tree_pool.nodes_samples, n, 1)) / len(self.tree_pool.nodes_samples)
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
            s = query_score(q, self.tree_pool.nodes_samples,
                            set(node_samples) - {q})
            return s
        if False:
            from tqdm import tqdm
            e = {q: score(q) for q in tqdm(self._cand_pool)}
        else:
            q2score = {q: score(q) for q in self._cand_pool}
        # top = 10
        # top_qs = list(sorted(q2score, key=q2score.__getitem__))[:top]

        # print('top score queries:')
        # for q in top_qs:
        #     print('{}({:.2f})'.format(q, q2score[q]))
            
        best_q = min(self._cand_pool, key=q2score.__getitem__)
        # print('best_q', best_q)
        return best_q
