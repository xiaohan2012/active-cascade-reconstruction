import pytest
import numpy as np

from core import uncertainty_scores, sample_steiner_trees
from sample_pool import TreeSamplePool
from graph_helpers import is_steiner_tree
from tree_stat import TreeBasedStatistics
from fixture import g, gi, obs


@pytest.mark.parametrize("normalize_p", ['div_max', None])
def test_uncertainty_scores(g, gi, obs, normalize_p):
    estimator = TreeBasedStatistics(g)
    sampler = TreeSamplePool(g, 25, 'cut', gi=gi,
                             return_tree_nodes=True)
    sampler.fill(obs)

    scores = uncertainty_scores(g, obs, sampler, estimator,
                                normalize_p=normalize_p)
    
    with pytest.raises(KeyError):
        for o in obs:
            scores[o]
    remain_nodes = set(np.arange(g.num_vertices())) - set(obs)
    for u in remain_nodes:
        assert scores[u] >= 0
        

@pytest.mark.parametrize("return_tree_nodes", [True, False])
@pytest.mark.parametrize("method", ['cut_naive', 'cut', 'loop_erased'])
def test_sample_steiner_trees(g, gi, obs, return_tree_nodes, method):
    n_samples = 100
    st_trees_all = sample_steiner_trees(g, obs, method, n_samples,
                                        gi=gi,
                                        return_tree_nodes=return_tree_nodes)
    assert len(st_trees_all) == n_samples

    for t in st_trees_all:
        if return_tree_nodes:
            assert set(obs).issubset(t)
        else:
            assert is_steiner_tree(t, obs)
