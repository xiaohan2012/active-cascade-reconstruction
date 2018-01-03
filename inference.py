import numpy as np
from minimum_steiner_tree import min_steiner_tree
from core import node_occurrence_freq
from graph_helpers import extract_nodes


def infection_probability(g, obs, sampler):
    """
    infer infection probability over nodes given `obs` and using `sampler`
    """
       
    # subset_size = kwargs.get('subset_size', None)
    # if 'st_trees' in kwargs:
    #     st_trees = kwargs['st_trees']
    # elif 'sp_trees' in kwargs:
    #     sp_trees = kwargs['sp_trees']
    #     st_trees = sample_steiner_trees(g, obs,
    #                                     subset_size=subset_size,
    #                                     sp_trees=sp_trees)
    # else:
    #     n_samples = kwargs['n_samples']
    #     st_trees = sample_steiner_trees(g, obs, n_samples,
    #                                     subset_size=subset_size,
    #                                     sp_trees=None)
    if sampler.is_empty:
        sampler.fill(obs)
    n_nodes = len(g._Graph__filter_state['vertex_filter'][0].a)
    remainig_nodes = extract_nodes(g)

    proba_values = np.array([node_occurrence_freq(n, sampler.samples)[0]
                             for n in remainig_nodes]) / sampler.n_samples
    inf_probas = np.zeros(n_nodes)
    inf_probas[remainig_nodes] = proba_values
    return inf_probas


def infer_infected_nodes(g, obs, sampler=None, use_proba=True,
                         method="min_steiner_tree", min_inf_proba=0.5):
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
        assert sampler is not None, 'sampling approach requires a sampler'
        inf_probas = infection_probability(g, obs, sampler)
        if use_proba:
            return inf_probas
        else:
            return (inf_probas >= min_inf_proba).nonzero()[0]
