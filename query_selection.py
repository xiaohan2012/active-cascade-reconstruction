import numpy as np
import random
from core import uncertainty_scores
from graph_tool.centrality import pagerank


class BaseQueryGenerator():
    def __init__(self, g, obs):
        self.pool = set(np.arange(g.num_vertices())) - set(obs)

    def select_query(self, *args, **kwargs):
        assert self.pool, 'no more node to query'
        q = self._select_query(*args, **kwargs)
        self.pool.remove(q)
        return q

    def _select_query(self, *args, **kwargs):
        raise NotImplementedError('do it yourself!')

    def empty(self):
        return len(self.pool) == 0


class RandomQueryGenerator(BaseQueryGenerator):
    """random query generator"""

    def _select_query(self, *args, **kwargs):
        return random.choice(list(self.pool))


class OurQueryGenerator(BaseQueryGenerator):
    """OUR CONTRIBUTION"""
    def __init__(self, *args, num_spt=100, num_stt=25, method='count'):
        self.num_spt = num_spt
        self.num_stt = num_stt
        self.method = method
        super(OurQueryGenerator, self).__init__(*args)

    def _hide_isolated_nods(self, g):
        iso_nodes = np.nonzero(g.degree_property_map('out').a == 0)[0]
        vfilt = g.get_vertex_filter()[0]
        for v in iso_nodes:
            vfilt[v] = False
        g.set_vertex_filter(vfilt)
        
    def _show_all_nodes(self, g):
        "show all nodes"""
        vfilt = g.get_vertex_filter()[0]
        vfilt.a = True
        g.set_vertex_filter(vfilt)
        
    def _select_query(self, g, inf_nodes):
        """we need to ensure all visible nodes in `g` are in the same component
        because of the node/query isolation process during active learning, edges are removed
        thus, there might not be spanning tree the new graph
        to solve this issue, we need to hide the isolated nodes, so there is spanning tree
        and we are done with the query selection
        we reveal those hidden nodes

        why this hassle? because `inference.infer_infected_nodes` requires all nodes are shown
        """
        
        # hide
        self._hide_isolated_nods(g)
        
        scores = uncertainty_scores(
            g, inf_nodes,
            self.num_spt,
            self.num_stt,
            self.method)
        q = max(self.pool, key=scores.__getitem__)

        # show
        self._show_all_nodes(g)
        return q


class PRQueryGenerator(BaseQueryGenerator):
    """rank node by pagerank score
    """
    def __init__(self, g, obs, *args, **kwargs):
        # personalized vector for pagerank
        pers = g.new_vertex_property('float')
        for o in obs:
            pers[o] = 1 / len(obs)
        rank = pagerank(g, pers=pers)

        self.pr = {}
        for v in g.vertices():
            self.pr[int(v)] = rank[v]
            
        super(PRQueryGenerator, self).__init__(g, obs, *args, **kwargs)

    def _select_query(self):
        return max(self.pool, key=self.pr.__getitem__)
