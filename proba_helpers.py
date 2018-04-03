import numpy as np
from collections import Counter

from random_steiner_tree import random_steiner_tree

from graph_helpers import swap_end_points


def tree_probability_gt(out_degree, p_dict, edges):
    numer = np.product([p_dict[(u, v)] for u, v in edges])
    denum = np.product([out_degree[u] for u, _ in edges])
    assert denum > 0, [out_degree[u] for u, _ in edges]
    return numer / denum


def casccade_probability_gt(p_dict, casdade_edges):
    return np.product([p_dict[(u, v)] for u, v in casdade_edges])


def tree_probability_nx(g, edges):
    numer = np.product([g[u][v]['weight'] for u, v in edges])
    denum = np.product([g.out_degree(u, weight='weight') for u, v in edges])
    return numer / denum


def casccade_probability_nx(g, casdade_edges):
    return np.product([g[u][v]['weight'] for u, v in casdade_edges])


def sampled_tree_freqs(gi, X, root, sampling_method, N):
    trees = [swap_end_points(random_steiner_tree(gi, X, root, method=sampling_method))
             for i in range(N)]
    tree_freq = Counter(trees)
    return tree_freq


def ic_cascade_probability_gt(g, p_dict, cascade_edges, nbr_dict):
    probas_from_active_edges = np.product([p_dict[(u, v)] for u, v in cascade_edges])
    inactive_edges = {(u, int(w))
                      for u, v in cascade_edges
                      for w in nbr_dict[u]
                      if v != w}
    inactive_edges -= set(cascade_edges)
    probas_from_inactive_edges = np.product([p_dict[(u, v)] for u, v in inactive_edges])
    return probas_from_active_edges * probas_from_inactive_edges
