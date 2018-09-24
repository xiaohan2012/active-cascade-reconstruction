import pytest
import numpy as np
from inference import infection_probability
from graph_helpers import (gen_random_spanning_tree, extract_nodes,
                           remove_filters,
                           observe_uninfected_node)
from random_steiner_tree.util import isolate_vertex
from sample_pool import TreeSamplePool
from tree_stat import TreeBasedStatistics
from fixture import g, gi, obs


def test_inf_probas_shape(g, gi, obs):
    """might fail if the removed vertex isolates some observed nodes
    """
    error_estimator = TreeBasedStatistics(g)
    sampler = TreeSamplePool(g, 25, 'cut', gi=gi,
                             return_type='nodes')
    sampler.fill(obs)
    error_estimator.build_matrix(sampler.samples)

    n = g.num_vertices()
    all_nodes = extract_nodes(g)
    remaining_nodes = list(set(all_nodes) - set(obs))

    # remove five nodes
    removed = []
    for i in range(5):
        r = remaining_nodes[i]
        removed.append(r)

        observe_uninfected_node(g, r, obs)
        isolate_vertex(gi, r)

        # update samples
        new_samples = sampler.update_samples(obs, {r: 0})
        error_estimator.update_trees(new_samples, {r: 0})

        # check probas
        probas = error_estimator.unconditional_proba()

        assert probas.shape == (n,)
        for r in removed:
            assert probas[r] == 0
        for o in obs:
            assert probas[o] == 1.0
