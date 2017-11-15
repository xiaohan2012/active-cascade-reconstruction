import numpy as np
from minimum_steiner_tree import min_steiner_tree
from core import sample_steiner_trees, node_occurrence_freq
from graph_helpers import extract_nodes


def infection_probability(g, obs, **kwargs):
    """
    `kwargs` has 3 cases:

    1. `st_trees`: steiner tree samples, so no need to sample them
    2. `sp_trees`: spanning tree samples, need to extract steiner trees
    3. no trees: then we sample `n_samples` steiner trees
    """
       
    subset_size = kwargs.get('subset_size', None)
    if 'st_trees' in kwargs:
        st_trees = kwargs['st_trees']
    elif 'sp_trees' in kwargs:
        sp_trees = kwargs['sp_trees']
        st_trees = sample_steiner_trees(g, obs,
                                        subset_size=subset_size,
                                        sp_trees=sp_trees)
    else:
        n_samples = kwargs['n_samples']
        st_trees = sample_steiner_trees(g, obs, n_samples,
                                        subset_size=subset_size,
                                        sp_trees=None)
    n_nodes = len(g._Graph__filter_state['vertex_filter'][0].a)
    remainig_nodes = extract_nodes(g)
    # print(remainig_nodes)
    proba_values = np.array([node_occurrence_freq(n, st_trees)[0]
                             for n in remainig_nodes]) / len(st_trees)
    inf_probas = np.zeros(n_nodes)
    inf_probas[remainig_nodes] = proba_values
    return inf_probas


def infer_infected_nodes(g, obs, use_proba=True, method="min_steiner_tree", **kwargs):
    """besides observed infections, infer other infected nodes
    if method is 'sampling', refer to infection_probability,

    `min_inf_proba` is the minimum infection probability to be considered "'infected'
    """
    assert method in {"min_steiner_tree", "sampling"}
    if method == 'min_steiner_tree':
        st = min_steiner_tree(g, obs)
        remain_infs = set(map(int, st.vertices()))
        return remain_infs
    else:  # sampling
        inf_probas = infection_probability(g, obs, **kwargs)
        if use_proba:
            return inf_probas
        else:
            min_inf_proba = kwargs.get('min_inf_proba', 0.5)
            return (inf_probas >= min_inf_proba).nonzero()[0]
