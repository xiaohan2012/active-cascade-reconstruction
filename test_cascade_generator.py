import pytest
from graph_tool import Graph
from cascade_generator import get_infection_time
from numpy.testing import assert_array_equal


@pytest.fixture
def g():
    g = Graph(directed=False)
    g.add_vertex(4)
    g.add_edge_list([(0, 1), (1, 2), (2, 3)])
    return g


def test_get_infection_time(g):
    time, edge_list = get_infection_time(g, 0, return_edges=True)
    assert set(edge_list) == {(0, 1), (1, 2), (2, 3)}
    assert_array_equal(time, [0, 1, 2, 3])
