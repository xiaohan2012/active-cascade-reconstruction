import pytest
import random
import numpy as np

from copy import copy
from core import uncertainty_scores, sample_steiner_trees
from sample_pool import TreeSamplePool
from graph_helpers import is_steiner_tree
from tree_stat import TreeBasedStatistics
from graph_helpers import observe_uninfected_node
from random_steiner_tree.util import isolate_vertex
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


@pytest.mark.parametrize("method", ['cut', 'loop_erased'])
@pytest.mark.parametrize("edge_weight", [1.0, 0.5])
def test_TreeSamplePool_with_incremental_sampling(g, gi, obs, method, edge_weight):
    
    edge_weights = g.new_edge_property("float")
    edge_weights.set_value(edge_weight)  # for sure to include all nodes
    
    n_samples = 100
    sampler = TreeSamplePool(g, n_samples, method,
                             edge_weights=edge_weights,
                             gi=gi,
                             return_tree_nodes=True,
                             with_inc_sampling=True)

    sampler.fill(obs)

    assert len(sampler.samples) == n_samples

    for t in sampler.samples:
        assert isinstance(t, set)
        assert set(obs).issubset(t)
        if edge_weight == 1.0:
            # if edge weight is 1, all nodes are infected
            assert len(t) == g.num_vertices()

    # update
    n = random.choice(
        list(set(np.arange(g.num_vertices())) - set(obs)))
    isolate_vertex(gi, n)
    observe_uninfected_node(g, n, obs)

    num_invalid_trees = sum(1 for t in sampler.samples if n in t)
    valid_trees = [t
                   for t in sampler.samples
                   if n not in t]  # this tree cannot be changed even after .update
    valid_trees_old = copy(valid_trees)
    
    new_samples = sampler.update_samples(obs, n, 0)
    
    assert len(sampler.samples) == n_samples

    assert len(new_samples) == num_invalid_trees
    
    for t in new_samples:
        # new samples are also incremented
        assert isinstance(t, set)
        assert set(obs).issubset(t)
        if edge_weight == 1.0:
            assert len(t) == g.num_vertices()  # now it's 99

    # make sure valid trees before and after update remaint the same
    for t1, t2 in zip(valid_trees, valid_trees_old):
        assert t1 == t2
