import numpy as np
import random
from scipy.stats import entropy

from linalg_helpers import num_spanning_trees_dense
from graph_helpers import (contract_graph_by_nodes,
                           extract_nodes, extract_steiner_tree,
                           has_vertex, gen_random_spanning_tree,
                           filter_graph_by_edges)
from inference import infection_probability
from tqdm import tqdm
from random_steiner_tree import random_steiner_tree

# @profile
def det_score_of_steiner_tree(st, g):
    """
    Param:
    --------
    st: GraphView, steiner tree
    
    Returns:
    --------
    returns its score of being sampled by the truncate algorithm
    
    the score is computed as the determinant of the contracted graph of g on st.vertices()
    """
    cg, weights = contract_graph_by_nodes(g, extract_nodes(st))
    return num_spanning_trees_dense(cg, weights)


def resample(steiner_trees, g, m):
    """resample the trees with probability proportional to their real score / determinant score
    m: number of sub-samples to draw
    """
    det_scores = [det_score_of_steiner_tree(st, g)
                  for st in steiner_trees]
    real_scores = np.exp([-st.num_edges() for st in steiner_trees])
    sampling_importance = real_scores / np.array(det_scores)
    sampling_importance /= sampling_importance.sum()

    resampled_ids = np.random.choice(np.arange(len(steiner_trees)), m, replace=False, p=sampling_importance)
    return [steiner_trees[i] for i in resampled_ids]

# @profile
def node_occurrence_freq(n, trees):
    """count how many times node `n` occures in `trees`
    returns (int, int), (yes it is in, not it's not)
    """
    yes, no = 0, 0
    for t in trees:
        if isinstance(t, set):
            if n in t:
                yes += 1
            else:
                no += 1
        else:
            if has_vertex(t, n):
                yes += 1
            else:
                no += 1
    return yes, no


def uncertainty_entropy(n, trees):
    yes, no = node_occurrence_freq(n, trees)
    p = np.array([yes, no], dtype=np.float32)
    p /= p.sum()
    return entropy(p)


def uncertainty_count(n, trees):
    yes, no = node_occurrence_freq(n, trees)
    return min(yes, no)

# @profile
def sample_steiner_trees(g, obs,
                         method,
                         n_samples,
                         gi=None,
                         root_sampler=None,
                         return_tree_nodes=False):
    """sample `n_samples` steiner trees that span `obs` in `g`

    `method`: the method for sampling steiner tree
    `n_samples`: sample size
    `gi`: the Graph object that is used if `method` in {'cut', 'loop_erased'}
    `root_sampler`: function that samples a root
    `return_tree_nodes`: if True, return the set of nodes that are in the sampled steiner tree
    """
    assert method in {'cut', 'cut_naive', 'loop_erased'}

    steiner_tree_samples = []
    # for i in tqdm(range(n_samples), total=n_samples):
    for i in range(n_samples):
        if root_sampler is None:
            # print('random root')
            # note: isolated nodes *should* be masked
            root = int(random.choice(list(g.vertices())))
        else:
            # print('custom root sampler')
            assert callable(root_sampler), 'root_sampler should be callable'
            root = root_sampler()

        if method == 'cut_naive':
            rand_t = gen_random_spanning_tree(g, root=root)
            st = extract_steiner_tree(rand_t, obs, return_nodes=return_tree_nodes)
            # if return_tree_nodes:
            #     st = set(map(int, st.vertices()))
        elif method in {'cut', 'loop_erased'}:
            assert gi is not None
            edges = random_steiner_tree(gi, obs, root, method)
            if return_tree_nodes:
                st = set(u for e in edges for u in e)
            else:
                st = filter_graph_by_edges(g, edges)

        steiner_tree_samples.append(st)

    return steiner_tree_samples


# @profile
def uncertainty_scores_old(g, obs,
                           sampler,
                           method='count'):
    """
    calculate uncertainty scores based on sampled steiner trees

    Args:

    Graph `g`
    list of int `obs`: list of observed nodes
    sampler: the tree sampler
    str `method`: {'count', 'entropy'}

    Returns:

    dict of (int, float): node to uncertainty score
    """
    if sampler.is_empty:
        sampler.fill(obs)
    
    if method == 'count':
        uncert = uncertainty_count
    elif method == 'entropy':
        uncert = uncertainty_entropy
    else:
        raise ValueError('unknown method')
    
    non_obs_nodes = set(extract_nodes(g)) - set(obs)
    r = {n: uncert(n, sampler.samples)
         for n in non_obs_nodes}
    return r


def uncertainty_scores(g, obs,
                       sampler,
                       error_estimator,
                       method='count'):
    """
    calculate uncertainty scores based on sampled steiner trees

    Args:

    Graph `g`
    list of int `obs`: list of observed nodes
    sampler: the tree sampler
    error_estimator: what does the actual counting
    str `method`: {'count', 'entropy'}

    Returns:

    dict of (int, float): node to uncertainty score
    """
    if sampler.is_empty:
        sampler.fill(obs)

    p = infection_probability(g, obs, sampler, error_estimator)
    print(p)
    non_obs_nodes = set(extract_nodes(g)) - set(obs)

    uncert = [entropy([v, 1-v]) for v in p]
    print(uncert)
    r = {n: uncert[n]
         for n in non_obs_nodes}
    return r
