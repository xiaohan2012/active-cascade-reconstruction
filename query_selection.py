import random
from core import uncertainty_scores
from graph_tool.centrality import pagerank
from graph_helpers import extract_nodes


class BaseQueryGenerator():
    def __init__(self, g, obs):
        self._pool = set(extract_nodes(g)) - set(obs)

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


class OurQueryGenerator(BaseQueryGenerator):
    """OUR CONTRIBUTION"""
    def __init__(self, *args, num_spt=100, num_stt=25, method='count'):
        self.num_spt = num_spt
        self.num_stt = num_stt
        self.method = method
        super(OurQueryGenerator, self).__init__(*args)

    def _select_query(self, g, inf_nodes):
        scores = uncertainty_scores(
            g, inf_nodes,
            self.num_spt,
            self.num_stt,
            self.method)
        q = max(self._pool, key=scores.__getitem__)
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
        return max(self._pool, key=self.pr.__getitem__)
