import random
import math
import numpy as np

from graph_tool import GraphView, PropertyMap
from graph_tool.topology import shortest_distance
from graph_tool.search import bfs_search

from tqdm import tqdm

from helpers import infected_nodes, sampling_weights_by_order
from graph_helpers import BFSNodeCollector, reverse_bfs
from si import si_opt as si

MAXINT = np.iinfo(np.int32).max


def observe_cascade(c, source, q, method='uniform',
                    tree=None, source_includable=False):
    """
    given a cascade `c` and `source`,
    return a list of observed nodes according to probability `q`

    """
    all_infection = np.nonzero(c != -1)[0]
    if not source_includable:
        all_infection = list(set(all_infection) - {source})
    num_obs = int(math.ceil(len(all_infection) * q))

    # if num_obs < 2:
    #     num_obs = 2

    if method == 'uniform':
        return np.random.permutation(all_infection)[:num_obs]
    elif method == 'late':
        return np.argsort(c)[-num_obs:]
    elif method == 'leaves':
        assert tree is not None, 'to get the leaves, the cascade tree is required'
        # extract_steiner_tree(tree, )
        nodes_in_order = reverse_bfs(tree)
        return nodes_in_order[:num_obs]
    elif method == 'bfs-head':
        assert tree is not None, 'the cascade tree is required'
        vis = BFSNodeCollector()
        bfs_search(GraphView(tree, directed=False), source, vis)
        sampling_weights_by_order
        vis.nodes_in_order
        return vis.nodes_in_order[:num_obs]  # head
    elif method == 'bfs-tail':
        assert tree is not None, 'the cascade tree is required'
        vis = BFSNodeCollector()
        bfs_search(GraphView(tree, directed=False), source, vis)
        return vis.nodes_in_order[-num_obs:]  # tail
    else:
        raise ValueError('unknown method {}'.format(method))


def sample_graph_by_p(g, p):
    """
    for IC model
    graph_tool version of sampling a graph
    mask the edge according to probability p and return the masked graph

    g: the graph
    p: float or np.array
    """
    if isinstance(p, PropertyMap):
        p = p.a
    flags = (np.random.random(g.num_edges()) <= p)
    p = g.new_edge_property('bool')
    p.set_2d_array(flags)
    return GraphView(g, efilt=p)


def get_infection_time(g, source, return_edges=False):
    """for IC model
    """
    time, pred_map = shortest_distance(g, source=source, pred_map=True)
    time = np.array(time.a)
    time[time == MAXINT] = -1
    if return_edges:
        edges = []
        reached = infected_nodes(time)
        for v in reached:
            # print(v)
            if pred_map[v] >= 0 and pred_map[v] != v:
                edges.append((pred_map[v], v))
        return time, edges
    else:
        return time


def ic(g, p, source=None, return_tree_edges=False,
       min_size=0, max_size=1e10):
    """
    graph_tool version of simulating cascade
    return np.ndarray on vertices as the infection time in cascade
    uninfected node has dist -1
    """
    if source is None:
        source = random.choice(np.arange(g.num_vertices(), dtype=int))
    gv = sample_graph_by_p(g, p)

    times = get_infection_time(gv, source, return_edges=False)
    size = len(infected_nodes(times))

    if size < min_size or size > max_size:
        # size does not fit
        # early stopping to save time
        return source, times, None
    
    stuff = get_infection_time(gv, source, return_edges=return_tree_edges)

    if not return_tree_edges:
        times = stuff
        tree_edges = None
    else:
        times, tree_edges = stuff
        # tree = filter_graph_by_edges(gv, tree_edges)
    
    return source, times, tree_edges
