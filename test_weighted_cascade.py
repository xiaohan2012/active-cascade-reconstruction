import pytest
import numpy as np
from graph_helpers import load_graph_by_name
from helpers import infected_nodes
from experiment import gen_input
from itertools import combinations

@pytest.fixture
def g():
    return load_graph_by_name('grqc', weighted=True)


@pytest.mark.parametrize("cascade_model", ['si', 'ic'])
@pytest.mark.parametrize("weighted", [True, False])
@pytest.mark.parametrize("source", [np.random.choice(1000) for i in range(5)])
def test_gen_input(g, cascade_model, weighted, source):
    if weighted:
        p = g.edge_properties['weights']
    else:
        p = 0.8
    
    rows = [gen_input(g, p=p, model=cascade_model, source=source, stop_fraction=0.1)
            for i in range(10)]

    # make sure no two cascades are the same
    # with low probability, this fails
    for r1, r2 in combinations(rows, 2):
        obs1, c1 = r1
        obs2, c2 = r2
        assert set(obs1) != set(obs2)

    # check for cascade size
    # only applicable for SI model
    if cascade_model == 'si':
        for r in rows:
            c = r[1]
            frac = len(infected_nodes(c)) / g.num_vertices()
            assert frac <= 0.11
