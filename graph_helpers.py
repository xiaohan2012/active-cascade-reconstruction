import numpy as np
import itertools
from copy import copy
from collections import defaultdict
from itertools import repeat

from graph_tool import Graph, GraphView, load_graph
from graph_tool.search import bfs_search, BFSVisitor
from graph_tool.generation import lattice
from graph_tool.topology import random_spanning_tree, label_components


def build_graph_from_edges(edges):
    """returns Graph (a new one)
    """
    g = Graph()
    for u, v in edges:
        g.add_edge(u, v)
    return g


def filter_graph_by_edges(g, edges):
    """returns GraphView
    """
    efilt = g.new_edge_property('bool')
    efilt.set_value(False)
    for i, j in edges:
        efilt[g.edge(i, j)] = True

    vfilt = g.new_vertex_property('bool')
    vfilt.set_value(False)
    for e in edges:
        for u in e:
            vfilt[u] = True

    return GraphView(g, efilt=efilt, vfilt=vfilt)


def get_leaves(t):
    assert t.is_directed() is False
    return np.nonzero(t.degree_property_map(deg='out').a == 1)[0]


def extract_nodes(g):
    return [int(u) for u in g.vertices()]


def extract_edges(g):
    return [(int(u), int(v)) for u, v in g.edges()]

# @profile
def extract_steiner_tree(sp_tree, terminals, return_nodes=True):
    """given spanning tree and terminal nodes, extract the minimum steiner tree that spans terminals
    
    Args:
    ------------

    sp_tree: spanning tree
    terminals: list of integers
    return_nodes: bool, return set<int> if True, GraphView otherwise

    Return:
    -----------
    GraphView | sec<int>: the steiner tree or the set of nodes
    
    algorithm idea:

    1. BFS from any `s \in terminals`, to the other terminals, `terminals - {s}`
    2. traverse back from each `v \in terminals-{s}` to s and collect the edges
       - note that traversal is terminated if some node is already traversed
         (in other words, edges are added already)

    running time: O(E)
    """
    terminals = copy(terminals)  # iterative use of obs

    if not isinstance(terminals, list):
        terminals = list(set(terminals))

    assert len(terminals) > 0

    # predecessor map, int -> int
    pred = dict(zip(extract_nodes(sp_tree),
                    itertools.repeat((-1, None))))

    class Visitor(BFSVisitor):
        """record the predecessor"""

        def __init__(self, pred):
            self.pred = pred
        
        def tree_edge(self, e):
            # optimization here
            # stores (source, edge)
            # because getting edge is expensive in graph_tool
            self.pred[int(e.target())] = (int(e.source()), e)
    
    vis = Visitor(pred)

    st_edges = set()
    
    visited = dict(zip(extract_nodes(sp_tree),
                       repeat(False)))

    nodes_visited = set()
    s = terminals[0]
    bfs_search(sp_tree, source=s, visitor=vis)

    while len(terminals) > 0:
        x = terminals.pop()
        nodes_visited.add(x)
        if visited[x]:
            continue
        
        visited[x] = True
        
        # get edges from x to s
        y, e = vis.pred[x]
        while y >= 0:
            nodes_visited.add(y)
            # 0 can be node, `while y` is wrong
            st_edges.add(e)

            if visited[y]:
                break
            
            visited[y] = True
            x = y
            y, e = vis.pred[x]

    if return_nodes:
        return nodes_visited
    else:
        vfilt = sp_tree.new_vertex_property('bool')
        vfilt.a = False
        for v, flag in visited.items():
            if flag:
                vfilt.a[v] = True

        efilt = sp_tree.new_edge_property('bool')
        efilt.a = False

        for e in st_edges:
            efilt[e] = True

        return GraphView(sp_tree, vfilt=vfilt, efilt=efilt)


def gen_random_spanning_tree(g, root=None):
    efilt = random_spanning_tree(g, root=root)
    return GraphView(g, efilt=efilt)

# @profile
def contract_graph_by_nodes(g, nodes, weights=None):
    """
    contract graph by nodes (only for undirected)

    note: the supernode is node 0 in the new graph

    Params:
    ----------
    g: Graph, undirected
    weights: edge_property_map
    nodes: list of ints

    Returns:
    ----------
    - Graph: a contracted graph where `nodes` are merged into a supernode
    - edge_property_map: new weight
    """
    if len(nodes) == 1:
        return g, weights

    nodes = set(nodes)

    # print('nodes:', nodes)
    
    # re-align the nodes
    # `v \in nodes` are considered node 0
    # get the old node to new node mapping
    o2n_map = {}
    c = 1
    for v in g.vertices():
        v = int(v)
        if v not in nodes:
            o2n_map[v] = c
            c += 1
        else:
            o2n_map[v] = 0
    # print('o2n_map:', o2n_map)

    # calculate new edges and new weights
    e2w = defaultdict(float)
    for e in g.edges():
        u, v = map(int, [e.source(), e.target()])
        nu, nv = sorted([o2n_map[u], o2n_map[v]])
        if weights:
            e2w[(nu, nv)] += weights[g.edge(u, v)]
        else:
            e2w[(nu, nv)] += 1

    # print('e2w:', e2w)

    # create the new graph
    new_g = Graph(directed=False)
    # for _ in range(g.num_vertices() - len(nodes) + 1):
    #     new_g.add_vertex()

    edges = []
    for u, v in e2w:
        e = new_g.add_edge(u, v)
        edges.append(e)

    new_weights = new_g.new_edge_property('float')
    for e, w in zip(edges, e2w.values()):
        new_weights[e] = w

    return new_g, new_weights


def extract_edges_from_pred(source, target, pred):
    """edges from `target` to `source` using predecessor map, `pred`"""
    edges = []
    c = target
    while c != source and pred[c] != -1:
        edges.append((pred[c], c))
        c = pred[c]
    return edges


class DistPredVisitor(BFSVisitor):
    """visitor to track distance and predecessor"""

    def __init__(self, pred, dist):
        """np.ndarray"""
        self.pred = pred
        self.dist = dist

    def tree_edge(self, e):
        s, t = int(e.source()), int(e.target())
        self.pred[t] = s
        self.dist[t] = self.dist[s] + 1


def init_visitor(g, root):
    dist = defaultdict(lambda: -1)
    dist[root] = 0
    pred = defaultdict(lambda: -1)
    vis = DistPredVisitor(pred, dist)
    return vis


def is_tree(t):
    # num nodes = num edges+1
    if t.num_vertices() != (t.num_edges() + 1):
        return False

    # all nodes have degree > 0
    vs = list(map(int, t.vertices()))
    degs = t.degree_property_map('out').a[vs]
    if np.all(degs > 0) == 0:
        return False

    return True


def is_steiner_tree(t, X):
    if not is_tree(t):
        return False
    for x in X:
        if not has_vertex(t, x):
            return False
    return True


def isolate_node(g, n):
    """mask out adjacent edges to `n` in `g`
    **with side-effect**
    """
    efilt = g.get_edge_filter()[0]
    incident_edges = g.vertex(n).out_edges()

    for e in incident_edges:
        # print('isolate node: hiding {}'.format(e))
        efilt[e] = False
    g.set_edge_filter(efilt)


def hide_node(g, n):
    """mask out node `n`
    **with side-effect**
    """
    vfilt = g.get_vertex_filter()[0]
    vfilt[n] = False
    g.set_vertex_filter(vfilt)


def remove_filters(g):
    """
    remove all filters and add filter with all entries on

    so that we won't get null vertex_filter or edge_filter
    """
    efilt = g.new_edge_property('bool')
    efilt.a = True
    vfilt = g.new_vertex_property('bool')
    vfilt.a = True

    return GraphView(g, efilt=efilt, vfilt=vfilt, directed=False)


def hide_disconnected_components(g, pivots):
    """
    given a graph (might be disconnected) and some nodes (pivots) in it.

    hide the components in `g` in which no pivot is in

    **with side effect**
    """    
    prop = label_components(g)[0]
    v2c = {v: prop[v] for v in g.vertices()}
    c2vs = defaultdict(set)
    for v, c in v2c.items():
        c2vs[c].add(v)

    vs_to_show = set()
    for v in pivots:
        vs_to_show |= c2vs[v2c[v]]

    vfilt = g.get_vertex_filter()[0]
    vfilt.set_value(False)
    for v in vs_to_show:
        vfilt[v] = True
    g.set_vertex_filter(vfilt)


def observe_uninfected_node(g, n, obs):
    """wrapper of isolate_node and hide_disconnected_components
    with side effect
    """
    isolate_node(g, n)
    hide_disconnected_components(g, obs)


def load_graph_by_name(name):
    if name == 'lattice':
        shape = (10, 10)
        g = lattice(shape)
    else:
        g = load_graph('data/{}/graph.gt'.format(name))
    assert not g.is_directed()
    return remove_filters(g)  # add shell


class GraphWrapper():
    """for graph equality"""
    def __init__(self, g):
        self._g = g
        self._nodes = set(extract_nodes(g))
        self._edges = set(map(lambda e: tuple(sorted(e)), extract_edges(g)))
        
    def __eq__(self, other):
        return self._nodes == other._nodes and self._edges == other._edges
    
    def __ne(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(tuple(self._nodes | self._edges))


def has_vertex(g, i):
    # to avoid calling g.vertex
    return g._Graph__filter_state['vertex_filter'][0].a[i] > 0


def k_hop_neighbors(v, g, k):
    def aux(v, k, visited):
        assert k >= 0
        if k == 0:
            return set()
        else:
            nbrs = set()
            for u in g.get_out_neighbours(v):
                if u not in visited:
                    nbrs.add(u)
                    visited.add(u)
                    nbrs |= aux(u, k-1, visited)
            return nbrs

    visited = {v}
    return aux(v, k, visited)
