import numpy as np
from scipy.stats import entropy

from linalg_helpers import num_spanning_trees_dense
from graph_helpers import (contract_graph_by_nodes,
                           extract_nodes, extract_steiner_tree,
                           has_vertex, gen_random_spanning_tree,
                           filter_graph_by_edges)

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
    for i in range(n_samples):
        if root_sampler is None:
            root = np.random.randint(0, g.num_vertices())
        else:
            assert callable(root_sampler), 'root_sampler should be callable'
            root = root_sampler(g, obs)

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
def uncertainty_scores(g, obs,
                       num_spt=100, num_stt=25,
                       method='count',
                       use_resample=True,
                       steiner_tree_samples=None,
                       spanning_tree_samples=None):
    """
    calculate uncertainty scores based on sampled steiner trees

    Args:

    Graph `g`
    list of int `obs`: list of observed nodes
    int `num_spt`: number of spanning trees
    int `num_stt`: number of steiner trees
    str `method`: {'count', 'entropy'}
    bool `use_resample`: wheter use SIR or not
    steiner_tree_samples: list of steiner trees (*before* resampling)
    spanning_tree_samples: list of spanning trees already sampled (for sample reuse)

    Returns:

    dict of (int, float): node to uncertainty score
    """
    if steiner_tree_samples is None:
        steiner_tree_samples = sample_steiner_trees(g, obs, num_spt, sp_trees=spanning_tree_samples)

    if use_resample:
        # two sets of scores
        det_scores = [det_score_of_steiner_tree(st, g)
                      for st in steiner_tree_samples]
        real_scores = np.exp([-st.num_edges()
                              for st in steiner_tree_samples])

        # normalize into proba
        sampling_importance = real_scores / np.array(det_scores)
        sampling_importance /= sampling_importance.sum()

        # st trees to choose
        resampled_ids = np.random.choice(
            np.arange(len(steiner_tree_samples)), num_stt, replace=False,
            p=sampling_importance)

        tree_samples_resampled = [steiner_tree_samples[i]
                                  for i in resampled_ids]
    else:
        tree_samples_resampled = steiner_tree_samples

    if method == 'count':
        uncert = uncertainty_count
    elif method == 'entropy':
        uncert = uncertainty_entropy
    else:
        raise ValueError('unknown method')
    
    non_obs_nodes = set(extract_nodes(g)) - set(obs)
    r = {n: uncert(n, tree_samples_resampled)
         for n in non_obs_nodes}
    return r
