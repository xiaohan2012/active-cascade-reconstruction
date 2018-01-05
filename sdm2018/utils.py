from graph_tool.all import BFSVisitor, Graph


def extract_edges_from_pred(g, source, target, pred):
    """edges from target to source"""
    edges = []
    c = target
    while c != source and pred[c] != -1:
        edges.append((pred[c], c))
        c = pred[c]
    return edges


class MyVisitor(BFSVisitor):
    def __init__(self, pred, dist):
        """np.ndarray"""
        self.pred = pred
        self.dist = dist

    def black_target(self, e):
        t = int(e.target())
        if self.pred[t] == -1:
            s = int(e.source())
            self.pred[t] = s
            self.dist[t] = self.dist[s] + 1

    def tree_edge(self, e):
        s, t = e.source(), e.target()
        s, t = int(s), int(t)
        self.pred[t] = s
        self.dist[t] = self.dist[s] + 1


def init_visitor(g, root):
    # dist = np.ones(g.num_vertices()) * -1
    # pred = np.ones(g.num_vertices(), dtype=int) * -1
    
    dist = {i: -1.0 for i in range(g.num_vertices())}
    dist[root] = 0.0

    pred = {i: -1 for i in range(g.num_vertices())}
    return MyVisitor(pred, dist)


def earliest_obs_node(obs_nodes, infection_times):
    return min(obs_nodes, key=infection_times.__getitem__)


def filter_nodes_by_edges(t, edges):
    vfilt = t.new_vertex_property('bool')
    vfilt.a = False
    nodes = {u for e in edges for u in e}
    for n in nodes:
        vfilt[n] = True
    t.set_vertex_filter(vfilt)
    return t


def edges2graph(g, edges):
    tree = Graph(directed=True)
    for _ in range(g.num_vertices()):
        tree.add_vertex()
    for u, v in edges:
        tree.add_edge(int(u), int(v))

    return filter_nodes_by_edges(tree, edges)
