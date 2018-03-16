import random
import math
import numpy as np
from copy import copy

from graph_tool import Graph, GraphView, PropertyMap
from graph_tool.topology import shortest_distance

from helpers import infected_nodes


MAXINT = np.iinfo(np.int32).max


def observe_cascade(c, source, q, method='uniform', source_includable=False):
    """
    given a cascade `c` and `source`,
    return a list of observed nodes according to probability `q`

    """
    all_infection = np.nonzero(c != -1)[0]
    if not source_includable:
        all_infection = list(set(all_infection) - {source})
    num_obs = int(math.ceil(len(all_infection) * q))

    if num_obs < 2:
        num_obs = 2

    if method == 'uniform':
        return np.random.permutation(all_infection)[:num_obs]
    elif method == 'late':
        return np.argsort(c)[-num_obs:]


def si(g, p, source=None, stop_fraction=0.5):
    """
    g: the graph
    p: edge-wise infection probability
    stop_fraction: stopping if more than N x stop_fraction nodes are infected
    """
    weighted = False
    if isinstance(p, PropertyMap):
        weighted = True
    else:
        # is float and uniform
        assert 0 < p and p <= 1
        
    if source is None:
        source = random.choice(np.arange(g.num_vertices()))
    infected = {source}
    infection_times = np.ones(g.num_vertices()) * -1
    infection_times[source] = 0
    time = 0
    edges = []

    stop = False

    while True:
        infected_nodes_until_t = copy(infected)
        time += 1
        for i in infected_nodes_until_t:
            vi = g.vertex(i)
            for e in vi.all_edges():
                if weighted:
                    inf_proba = p[e]
                else:
                    inf_proba = p
                vj = e.target()
                j = int(vj)
                if j not in infected and random.random() <= inf_proba:
                    infected.add(j)
                    infection_times[j] = time
                    edges.append((i, j))

                    # stop when enough nodes have been infected
                    if (len(infected) / g.num_vertices()) >= stop_fraction:
                        stop = True
                        break
            if stop:
                break
        if stop:
            break
        
    tree = Graph(directed=True)
    for _ in range(g.num_vertices()):
        tree.add_vertex()
    for u, v in edges:
        tree.add_edge(u, v)
    return source, infection_times, tree


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
            print(v)
            if pred_map[v] >= 0 and pred_map[v] != v:
                edges.append((pred_map[v], v))
        return time, edges
    else:
        return time


def ic(g, p, source=None, return_edges=False):
    """
    graph_tool version of simulating cascade
    return np.ndarray on vertices as the infection time in cascade
    uninfected node has dist -1
    """
    if source is None:
        source = random.choice(np.arange(g.num_vertices(), dtype=int))
    gv = sample_graph_by_p(g, p)

    times = get_infection_time(gv, source)
    
    return source, times, None


def incremental_simulation(g, c, p, num_nodes, return_new_edges=False):
    """incrementally add edges to given cascade
    num_nodes is passed bacause vfilt might be passed
    """
    visited = {v: False for v in np.arange(num_nodes)}
    new_c = copy(c)
    for v in infected_nodes(c):
        visited[v] = True

    if return_new_edges:
        new_edges = []
        
    queue = list(infected_nodes(c))
    while len(queue) > 0:
        u = queue.pop(0)
        uu = g.vertex(u)
        for e in uu.out_edges():
            v = int(e.target())
            if np.random.random() <= p[e] and not visited[v]:  # active
                if return_new_edges:
                    new_edges.append((u, v))
                # print('adding node ', v)
                # print('len(new_c)', len(new_c))
                # print(len(c))
                new_c[v] = c[u] + 1
                visited[v] = True
                queue.append(v)

    if return_new_edges:
        return (new_c, new_edges)
    else:
        return new_c

