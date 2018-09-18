import pytest

import numpy as np
from sample_pool import SimulatedCascadePool
from test_helpers import check_tree_samples
from graph_helpers import observe_uninfected_node, extract_nodes
from fixture import g
from cascade_generator import si
from helpers import infected_nodes



def test_SimulatedCascadPool(g):
    n_samples = 10
    n_obs = 5
    cascade_params = dict(
        p=0.5,
        stop_fraction=0.5,
        cascade_model='si'
    )
    source, times, _ = si(
        g, source=None,
        p=cascade_params['p'],
        stop_fraction=cascade_params['stop_fraction']
    )
    inf_nodes = infected_nodes(times)
    obs = set(np.random.choice(inf_nodes, n_obs, replace=False))

    cascade_params['source'] = source

    pool = SimulatedCascadePool(g, n_samples, cascade_params)
    pool.fill(obs)

    for o in obs:
        for s in pool.samples:
            assert o in s

    assert len(pool.samples) == n_samples

    # node addition case
    node_to_add = list(set(inf_nodes) - obs)[0]
    pool.update_samples(obs | {node_to_add},
                        {node_to_add: 1})

    for s in pool.samples:
        assert node_to_add in s

    assert len(pool.samples) == n_samples

    # node removal case
    node_to_remove = list(pool.samples[0] - obs)[0]
    observe_uninfected_node(g, node_to_remove, obs)
    pool.update_samples(obs, {node_to_remove: 0})

    for s in pool.samples:
        assert node_to_remove not in s

    assert len(pool.samples) == n_samples
