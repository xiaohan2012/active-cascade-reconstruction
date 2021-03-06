import random
import pytest
import numpy as np
from sample_pool import SimulatedCascadePool
from graph_helpers import observe_uninfected_node
from fixture import g
from cascade_generator import ic
from helpers import infected_nodes



@pytest.mark.parametrize(
    "approach", ['mst', 'rst', 'rrs']  # 'naive'
)
def test_SimulatedCascadePool(g, approach):
    # 'naive', 
    n_samples = 10
    n_obs = 5
    cascade_params = dict(
        p=0.5,
        min_fraction=0.25,
        max_fraction=0.25,
        verbose=2
    )
    source, times, _ = ic(
        g, source=None,
        p=cascade_params['p'],
        min_fraction=cascade_params['min_fraction'],
        max_fraction=cascade_params['max_fraction']
    )
    inf_nodes = infected_nodes(times)
    obs = set(np.random.choice(inf_nodes, n_obs, replace=False))

    cascade_params['source'] = source

    pool = SimulatedCascadePool(
        g, n_samples,
        cascade_model='ic',
        approach=approach,
        cascade_params=cascade_params
    )
    pool.fill(obs)

    for o in obs:
        for s in pool.samples:
            assert o in s

    assert len(pool.samples) == n_samples

    # node addition case
    # add 10 nodes
    print("node addition case")
    for i in range(10):
        node_to_add = list(set(inf_nodes) - obs)[0]

        pool.update_samples(obs | {node_to_add},
                            {node_to_add: 1})

        for s in pool.samples:
            assert node_to_add in s

        assert len(pool.samples) == n_samples

    # node removal case
    # remove 10 nodes
    print("node removal case")
    for i in range(10):
        node_to_remove = random.choice(list(random.choice(pool.samples) - obs))

        observe_uninfected_node(g, node_to_remove, obs)

        if len(g.get_out_neighbours(source)) == 1:
            print('terminate early because of source is isoloated due to node deletion')
            break

        pool.update_samples(obs, {node_to_remove: 0})

        for s in pool.samples:
            assert node_to_remove not in s

        assert len(pool.samples) == n_samples
