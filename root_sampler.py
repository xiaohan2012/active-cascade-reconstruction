import numpy as np
import random
from graph_helpers import k_hop_neighbors, pagerank_scores


def build_earlier_root_sampler(g, obs, c, **kwargs):
    def f():
        return min(obs, key=lambda o: c[o])
    return f


def build_early_nbrs_sampler(g, obs, c, k=1, **kwargs):
    earliest_node = min(obs, key=lambda o: c[o])
    nbrs = list(k_hop_neighbors(earliest_node, g, k=k)) + [earliest_node]

    def f():
        return random.choice(nbrs)
    return f


def build_root_sampler_by_pagerank_score(g, obs, c, eps=0.0):
    pr_score = pagerank_scores(g, obs, eps)
    # print(g)
    # print('len(obs): ', len(obs))
    # print(pr_score)
    nodes = np.arange(len(pr_score))  # shapes should be consistent

    def aux():
        return np.random.choice(nodes, size=1, p=pr_score)[0]

    return aux
