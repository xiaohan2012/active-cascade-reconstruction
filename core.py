import random
import numpy as np
from scipy.stats import entropy

from linalg_helpers import num_spanning_trees_dense
from graph_helpers import (contract_graph_by_nodes,
                           extract_nodes, extract_steiner_tree,
                           gen_random_spanning_tree)


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


def node_occurrence_freq(n, trees):
    """count how many times node `n` occures in `trees`
    returns (int, int), (yes it is in, not it's not)
    """
    yes = 1  # smoothing
    no = 1
    for t in trees:
        try:
            t.vertex(n)
            yes += 1
        except ValueError:
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


def sample_steiner_trees(g, obs, n_samples):
    """sample `n_samples` steiner trees that span `obs` in `g`
    """
    steiner_tree_samples = []
    for _ in range(n_samples):
        rand_t = gen_random_spanning_tree(g)
        st = extract_steiner_tree(rand_t, obs)
        steiner_tree_samples.append(st)
    return steiner_tree_samples


# @profile
def uncertainty_scores(g, obs, steiner_tree_samples=None,
                       num_spt=100, num_stt=25,
                       method='count',
                       use_resample=True):
    """
    calculate uncertainty scores based on sampled steiner trees

    Args:

    Graph `g`
    list of int `obs`: list of observed nodes
    steiner_tree_samples: list of steiner trees (*before* resampling)
    int `num_spt`: number of spanning trees
    int `num_stt`: number of steiner trees
    str `method`: {'count', 'entropy'}
    bool `use_resample`: wheter use SIR or not

    Returns:

    dict of (int, float): node to uncertainty score
    """
    if steiner_tree_samples is None:
        steiner_tree_samples = sample_steiner_trees(g, obs, num_spt)

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
