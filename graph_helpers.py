import numpy as np
import itertools
from graph_tool import Graph, GraphView
from graph_tool.search import bfs_search, BFSVisitor


def build_graph_from_edges(edges):
    g = Graph()
    for u, v in edges:
        g.add_edge(u, v)
    return g


def get_leaves(t):
    assert t.is_directed() is False
    return np.nonzero(t.degree_property_map(deg='out').a == 1)[0]


def extract_nodes(g):
    return [int(u) for u in g.vertices()]


def extract_edges(g):
    return [(int(u), int(v)) for u, v in g.edges()]


def tree_by_edges(g, edges):
    efilt = g.new_edge_property('bool')
    efilt.set_value(False)
    for i, j in [(0, 1), (1, 2), (1, 3)]:
        efilt[g.edge(i, j)] = True
    return GraphView(g, efilt=efilt)


def extract_steiner_tree(sp_tree, X):
    """given spanning tree and terminal nodes, extract the steiner tree that spans X

    algorithm idea:

    1. BFS from `s \in X`, to the other terminals, `X - {s}`
    2. BFS back from `v \in X-{s}` to s and collect the edges
       - note that BFS is terminated if some node is already traversed
         (in other words, edges are added already)

    running time: O(E)
    """
    pred = dict(zip(range(sp_tree.num_vertices()), itertools.repeat(None)))

    class Visitor(BFSVisitor):
        """record the predecessor"""

        def __init__(self, pred):
            self.pred = pred
        
        def tree_edge(self, e):
            print(e)
            self.pred[int(e.target())] = int(e.source())
            print(self.pred)
    
    vis = Visitor(pred)
    
    efilt = sp_tree.new_edge_property('bool')
    efilt.set_value(False)

    vfilt = sp_tree.new_vertex_property('bool')
    vfilt.set_value(False)
    
    s = X.pop()
    bfs_search(sp_tree, source=s, visitor=vis)

    vfilt[s] = True
    while len(X) > 0:
        x = X.pop()
        vfilt[x] = True

        y = vis.pred[x]
        while y:
            efilt[sp_tree.edge(x, y)] = True
            vfilt[y] = True
            if not vfilt[y]:
                break
            x = y
            y = vis.pred[x]

    return GraphView(sp_tree, vfilt=vfilt, efilt=efilt)
