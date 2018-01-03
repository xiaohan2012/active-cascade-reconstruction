import pytest
from numpy.testing import assert_almost_equal
from graph_tool import Graph
from graph_tool.generation import complete_graph, lattice

from graph_helpers import (extract_steiner_tree, filter_graph_by_edges,
                           extract_edges, extract_nodes,
                           remove_filters,
                           contract_graph_by_nodes,
                           hide_disconnected_components)


@pytest.mark.parametrize("X,edges", [([1, 3], {(1, 3)}),
                                     ([0, 2], {(0, 1), (1, 2)}),
                                     ([0], set()),
                                     ([0, 1, 2, 3], {(0, 1), (1, 2), (1, 3)})])
def test_extract_steiner_tree(X, edges):
    g = complete_graph(4)
    tree = filter_graph_by_edges(g, [(0, 1), (1, 2), (1, 3)])

    # CASE 1
    # extract **tree**
    stt = extract_steiner_tree(tree, X, return_nodes=False)
    assert set(extract_edges(stt)) == edges

    if len(X) > 1:
        nodes = {u for e in edges for u in e}
        assert set(extract_nodes(stt)) == nodes
    else:
        # single terminal case
        assert set(extract_nodes(stt)) == set(X)

    # CASE 2
    # extract **nodes**
    stt = extract_steiner_tree(tree, X, return_nodes=True)
    if len(X) > 1:
        nodes = {u for e in edges for u in e}
        assert stt == nodes
    else:
        # single terminal case
        assert stt == set(X)


def test_contract_graph_by_nodes():
    def get_weight_by_edges(g, weights, edges):
        return [weights[g.edge(u, v)] for u, v in edges]
    
    # weighted graph
    g = lattice((2, 2))
    weights = g.new_edge_property('float')
    for e in g.edges():
        weights[e] = int(e.target())

    # contract 0 and 1
    cg, new_weights = contract_graph_by_nodes(g, [0, 1], weights)
    assert set(extract_nodes(cg)) == set(range(3))
    edges = [(0, 0), (0, 1), (0, 2), (1, 2)]
    assert set(extract_edges(cg)) == set(edges)
    assert_almost_equal(get_weight_by_edges(cg, new_weights, edges),
                        [1, 2, 3, 3])

    # contract 0, 1 and 2
    cg, new_weights = contract_graph_by_nodes(g, [0, 1, 2], weights)
    assert set(extract_nodes(cg)) == set(range(2))
    edges = [(0, 0), (0, 1)]
    assert set(extract_edges(cg)) == set(edges)
    assert_almost_equal(get_weight_by_edges(cg, new_weights, edges),
                        [3, 6])

    # contract all nodes
    cg, new_weights = contract_graph_by_nodes(g, [0, 1, 2, 3], weights)
    assert set(extract_nodes(cg)) == {0}
    assert set(extract_edges(cg)) == {(0, 0)}
    assert_almost_equal(new_weights.a, [9])

    # contract just 1
    cg, new_weights = contract_graph_by_nodes(g, [0], weights)
    assert set(extract_nodes(cg)) == set(extract_nodes(g))
    assert set(extract_edges(cg)) == set(extract_edges(g))
    assert_almost_equal(new_weights.a, weights.a)


def test_isolate_disconnected_components():
    ######### case 1 #######
    g = remove_filters(Graph(directed=False))
    g.add_vertex(4)
        
    hide_disconnected_components(g, [0, 2])  # 1, 3 are isolated
    assert set(extract_nodes(g)) == {0, 2}

    ######### case 2 #######
    g = remove_filters(Graph(directed=False))
    g.add_vertex(4)
    g.add_edge(0, 1)
    g.add_edge(1, 2)

    hide_disconnected_components(g, [0])
    assert set(extract_nodes(g)) == {0, 1, 2}
    


