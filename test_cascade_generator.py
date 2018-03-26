import pytest
import numpy as np
from graph_tool import Graph
from graph_helpers import extract_nodes, extract_edges
from cascade_generator import get_infection_time, ic, observe_cascade
from numpy.testing import assert_array_equal


@pytest.fixture
def g():
    g = Graph(directed=True)
    g.add_vertex(4)
    g.add_edge_list([(0, 1), (1, 2), (2, 3)])
    return g


@pytest.fixture
def p(g):
    p = g.new_edge_property('float')
    p.set_value(1.0)
    return p


def test_get_infection_time(g):
    time, edge_list = get_infection_time(g, 0, return_edges=True)
    assert set(edge_list) == {(0, 1), (1, 2), (2, 3)}
    assert_array_equal(time, [0, 1, 2, 3])


@pytest.mark.parametrize('return_tree_edges', [True, False])
def test_ic(g, p, return_tree_edges):
    source, time, tree_edges = ic(g, p, 0, return_tree_edges=return_tree_edges)

    assert source == 0
    assert_array_equal(time, [0, 1, 2, 3])

    if return_tree_edges:
        assert tree_edges == [(0, 1), (1, 2), (2, 3)]
    else:
        assert tree_edges is None


@pytest.fixture
def tree1():
    g = Graph(directed=True)
    g.add_vertex(5)  # one remaining singleton
    g.add_edge_list([(0, 1), (1, 2), (1, 3)])

    # to test 4 is not included
    vfilt = g.new_vertex_property('bool')
    vfilt.set_value(True)
    vfilt[4] = False
    g.set_vertex_filter(vfilt)
    return g


@pytest.mark.parametrize('tree, expected',
                         [(g(), [3]),
                          (tree1(), [2, 3])])
def test_observe_cascade_on_leaves(tree, expected):
    c = np.array([0, 1, 2, 3])  # dummy
    obs = observe_cascade(c,
                          None, q=1.0,
                          method='leaves',
                          tree=tree, source_includable=True)
    assert list(obs) == expected
