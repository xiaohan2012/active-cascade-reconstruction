import numpy as np
from minimum_steiner_tree import min_steiner_tree
from core import sample_steiner_trees, node_occurrence_freq
from graph_helpers import extract_nodes

def infer_infected_nodes(g, obs, method="min_steiner_tree", **kwargs):
    """besides observed infections, infer other infected nodes
    if method is 'sampling', then `kwargs` has 3 cases:

    1. `st_trees`: steiner tree samples, so no need to sample them
    2. `sp_trees`: spanning tree samples, need to extract steiner trees
    3. no trees: then we sample `n_samples` steiner trees
    
    `min_inf_proba` is the minimum infection probability to be considered "'infected'
    """
    assert method in {"min_steiner_tree", "sampling"}
    if method == 'min_steiner_tree':
        st = min_steiner_tree(g, obs)
        remain_infs = set(map(int, st.vertices()))
        return remain_infs
    else:
        if 'st_trees' in kwargs:
            st_trees = kwargs['st_trees']
        elif 'sp_trees' in kwargs:
            sp_trees = kwargs['sp_trees']
            st_trees = sample_steiner_trees(g, obs, sp_trees=sp_trees)
        else:
            n_samples = kwargs['n_samples']
            st_trees = sample_steiner_trees(g, obs, n_samples, sp_trees=None)

        min_inf_proba = kwargs.get('min_inf_proba', 0.5)
        inf_probas = np.array([node_occurrence_freq(n, st_trees)[0]
                               for n in extract_nodes(g)]) / len(st_trees)

        return (inf_probas >= min_inf_proba).nonzero()[0]
