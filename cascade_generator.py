import random
import math
import numpy as np
from copy import copy
from graph_tool import Graph


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
    if source is None:
        source = random.choice(np.arange(g.num_vertices()))
    infected = {source}
    infection_times = np.ones(g.num_vertices()) * -1
    infection_times[source] = 0
    time = 0
    edges = []
    while np.count_nonzero(infection_times != -1) / g.num_vertices() <= stop_fraction:
        infected_nodes_until_t = copy(infected)
        time += 1
        for i in infected_nodes_until_t:
            for j in g.vertex(i).all_neighbours():
                j = int(j)
                if j not in infected and random.random() <= p:
                    infected.add(j)
                    infection_times[j] = time
                    edges.append((i, j))

    tree = Graph(directed=True)
    for _ in range(g.num_vertices()):
        tree.add_vertex()
    for u, v in edges:
        tree.add_edge(u, v)
    return source, infection_times, tree