import pytest
from graph_tool import Graph
from graph_helpers import extract_nodes, extract_edges, get_edge_weights
from global_normalization import normalize_globally


@pytest.fixture
def g():
    g = Graph(directed=False)
    g.add_vertex(4)
    g.add_edge_list([(0, 1), (1, 3), (0, 2), (2, 3)])
    weights = g.new_edge_property('float')
    weights[g.edge(0, 1)] = 0.9
    weights[g.edge(1, 3)] = 0.8
    weights[g.edge(2, 3)] = 0.4
    weights[g.edge(0, 2)] = 0.1
    g.edge_properties['weights'] = weights
    return g


def test_normalize_globally(g):
    norm_g = normalize_globally(g)
    
    assert not norm_g.is_directed()

    max_w = 1.7
    expected_edges_and_weights = {
        (0, 1): 0.9 / max_w,
        (0, 2): 0.1 / max_w,
        (2, 3): 0.4 / max_w,
        (1, 3): 0.8 / max_w,
        # self-loops
        (0, 0): 0.7 / max_w,
        (1, 1): 0,
        (2, 2): 1.2 / max_w,
        (3, 3): 0.5 / max_w
    }
    assert norm_g.num_edges() == (g.num_edges() + g.num_vertices())
    assert set(extract_edges(norm_g)) == set(expected_edges_and_weights.keys())
    assert set(extract_nodes(norm_g)) == set(extract_nodes(g))

    new_edge_weights = get_edge_weights(norm_g)
    for (u, v), w in expected_edges_and_weights.items():
        assert pytest.approx(w) == new_edge_weights[norm_g.edge(u, v)]

    deg = norm_g.degree_property_map("out", new_edge_weights)
            
    for v in norm_g.vertices():
        # very stragely, self-loops are counted twice
        assert pytest.approx(1.0) == (deg[v] - new_edge_weights[norm_g.edge(v, v)])
