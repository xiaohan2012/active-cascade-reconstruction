import numpy as np
import random


class QueryGenerator():
    def __init__(self, g, obs):
        self.pool = set(np.arange(g.num_vertices())) - set(obs)

    def random(self):
        """random query"""
        assert self.pool, 'no more node to query'
        q = random.choice(list(self.pool))
        self.pool.remove(q)
        return q
