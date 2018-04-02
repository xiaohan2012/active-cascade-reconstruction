# coding: utf-8

import networkx as nx
import numpy as np
import pandas as pd
import random

from scipy.spatial.distance import cosine, cdist
from tqdm import tqdm
from collections import Counter
from itertools import combinations
from joblib import Parallel, delayed
from graph_tool import openmp_set_num_threads

from random_steiner_tree import random_steiner_tree
from random_steiner_tree.util import from_nx


def swap_end_points(edges):
    edges = [(v, u) for u, v in edges]  # pointing towards the root
    return tuple(sorted(edges))


def sampled_tree_freqs(gi, X, root, sampling_method, n_samples):
    tree_freq = Counter()
    for i in range(n_samples):
        t = swap_end_points(random_steiner_tree(gi, X, root, method=sampling_method))
        tree_freq[t] += 1
    # actual_probas = np.array(list(tree_freq.values())) / n_samples
    return tree_freq


def tree_proba(g, edges):
    numer = np.product([g[u][v]['weight'] for u, v in edges])
    denum = np.product([g.out_degree(u, weight='weight') for u, v in edges])
    
    return numer / denum


HIGH = 1
LOW = 0.0


def one_run(num_vertices, size_X, n_samples, low=LOW, high=HIGH):
    g = nx.complete_graph(num_vertices, create_using=nx.DiGraph())
    
    for u, v in g.edges_iter():
        g[u][v]['weight'] = (high - low) * np.random.random() + low

    gi = from_nx(g)

    if True:
        X = np.random.permutation(g.number_of_nodes())[:size_X]
        root = random.choice(list(set(g.nodes()) - set(X)))
    else:
        # root infects terminals
        X, root = min(g.edges_iter(), key=lambda e: g[e[0]][e[1]]['weight'])
        X = [X]

    # print('root = {}'.format(root))
    # print('terminals = {}'.format(X))
    # print(g[X[0]][root]['weight'])

    lerw_tree_freq = sampled_tree_freqs(gi, X, root, 'loop_erased', n_samples)

    cut_tree_freq = sampled_tree_freqs(gi, X, root, 'cut', n_samples)
    
    all_trees = set(lerw_tree_freq.keys()) | set(cut_tree_freq.keys())
    # print("num. unique trees: {}".format(len(all_trees)))

    lerw_actual_probas = np.array([lerw_tree_freq[t] / n_samples for t in all_trees])
    cut_actual_probas = np.array([cut_tree_freq[t] / n_samples for t in all_trees])

    expected_probas = np.array([tree_proba(g, t)
                                for t in all_trees])
    expected_probas /= expected_probas.sum()

    name_and_probas = [('True', expected_probas),
                       ('lerw', lerw_actual_probas),
                       ('cut', cut_actual_probas)]

    cosine_sims = {}
    abs_dists = {}
    for (n1, p1), (n2, p2) in combinations(name_and_probas, 2):
        # print('sim({}, {})={}'.format(n1, n2, 1-cosine(p1, p2)))
        cosine_sims[(n1, n2)] = 1-cosine(p1, p2)
        abs_dists[(n1, n2)] = cdist([p1], [p2], 'minkowski', p=1.0)[0, 0]
    return cosine_sims, abs_dists


if __name__ == '__main__':
    NUM_VERTICES = 8
    SIZE_X = 2
    N_SAMPLES = 10000000
    N_RUNS = 960

    openmp_set_num_threads(1)
    
    records = Parallel(n_jobs=-1)(
        delayed(one_run)(NUM_VERTICES, SIZE_X, n_samples=N_SAMPLES, low=LOW, high=HIGH)
        for i in tqdm(range(N_RUNS), total=N_RUNS))
    cosine_records, abs_records= zip(*records)

    cosine_df = pd.DataFrame.from_records(filter(None, cosine_records))
    abs_df = pd.DataFrame.from_records(filter(None, abs_records))
    print(cosine_df.describe())
    print(abs_df.describe())
    
