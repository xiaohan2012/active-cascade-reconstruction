import pytest
import random
import numpy as np

from copy import copy
from core import uncertainty_scores, sample_steiner_trees
from sample_pool import TreeSamplePool
from graph_helpers import is_steiner_tree
from tree_stat import TreeBasedStatistics
from graph_helpers import observe_uninfected_node
from random_steiner_tree.util import isolate_vertex, edges as gi_edges
from fixture import g, gi, obs


@pytest.mark.parametrize("normalize_p", ['div_max', None])
@pytest.mark.parametrize("sampling_method", ['cut', 'loop_erased'])
def test_uncertainty_scores(g, gi, obs, normalize_p, sampling_method):
    estimator = TreeBasedStatistics(g)
    sampler = TreeSamplePool(g, 25, sampling_method, gi=gi,
                             return_type='nodes')
    sampler.fill(obs)

    scores = uncertainty_scores(g, obs, sampler, estimator,
                                normalize_p=normalize_p)

    with pytest.raises(KeyError):
        for o in obs:
            scores[o]
    remain_nodes = set(np.arange(g.num_vertices())) - set(obs)
    for u in remain_nodes:
        assert scores[u] >= 0


@pytest.mark.parametrize("return_type", ['nodes', 'tuples', 'tree'])
@pytest.mark.parametrize("method", ['cut', 'loop_erased'])
def test_sample_steiner_trees(g, gi, obs, return_type, method):
    n_samples = 100
    st_trees_all = sample_steiner_trees(g, obs, method, n_samples,
                                        gi=gi,
                                        return_type=return_type)
    assert len(st_trees_all) == n_samples

    for t in st_trees_all:
        if return_type == 'nodes':
            assert set(obs).issubset(t)
        elif return_type == 'tree':
            assert is_steiner_tree(t, obs)
        elif return_type == 'tuples':
            assert isinstance(t, tuple)
        else:
            raise Exception
