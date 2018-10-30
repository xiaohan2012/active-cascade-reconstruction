import pytest
import numpy as np
from graph_helpers import load_graph_by_name
from helpers import infected_nodes
from cascade_generator import gen_input

from graph_tool import Graph
from itertools import combinations


@pytest.fixture
def g():
    return load_graph_by_name('grqc', weighted=True)


@pytest.mark.parametrize("cascade_model", ['si', 'ic'])
@pytest.mark.parametrize("weighted", [True, False])
@pytest.mark.parametrize("source", [np.random.choice(1000) for i in range(1)])
def test_gen_input(g, cascade_model, weighted, source):
    min_frac = 5. / g.num_vertices()
    max_frac = 0.1
    eps = 0.01
    if weighted:
        p = g.edge_properties['weights']
    else:
        p = g.new_edge_property('float')
        p.set_value(0.8)
    # print(cascade_model, weighted, source)
    rows = [
        gen_input(
            g, p=p, model=cascade_model, source=source,            
            min_fraction=min_frac,
            max_fraction=max_frac
        )
            for i in range(10)]

    # make sure no two cascades are the same
    # with low probability, this fails
    for r1, r2 in combinations(rows, 2):
        obs1, c1 = r1[:2]
        obs2, c2 = r2[:2]
        assert set(obs1) != set(list(obs2))

    # check for cascade size
    # only applicable for SI model
    for r in rows:
        c = r[1]
        frac = len(infected_nodes(c)) / g.num_vertices()
        assert frac <= (max_frac + eps)
