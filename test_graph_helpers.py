from graph_tool.generation import complete_graph


from graph_helpers import extract_steiner_tree, filter_graph_by_edges, extract_edges, extract_nodes


def test_extract_steiner_tree():
    g = complete_graph(4)
    tree = filter_graph_by_edges(g, [(0, 1), (1, 2), (1, 3)])

    stt = extract_steiner_tree(tree, [1, 3])
    assert extract_edges(stt) == [(1, 3)]
    assert set(extract_nodes(stt)) == {1, 3}

    stt = extract_steiner_tree(tree, [0, 2])
    assert set(extract_edges(stt)) == {(0, 1), (1, 2)}
    assert set(extract_nodes(stt)) == {0, 1, 2}

    stt = extract_steiner_tree(tree, [0])
    assert extract_edges(stt) == []
    assert extract_nodes(stt) == [0]

    stt = extract_steiner_tree(tree, [0, 1, 2, 3])
    assert set(extract_edges(stt)) == {(0, 1), (1, 2), (1, 3)}
    assert set(extract_nodes(stt)) == {0, 1, 2, 3}
