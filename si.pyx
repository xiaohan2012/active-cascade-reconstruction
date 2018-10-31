# optimized version of cascade generation functions
# using Cython

import numpy as np
import random
from graph_tool import (
    PropertyMap,
    Graph,
    load_graph
)
from copy import copy
from tqdm import tqdm

from graph_helpers import get_edge_weights

# C++ stuff
from libcpp cimport bool


cpdef si_opt(g, p, source=None, float min_fraction=0.0, float max_fraction=0.5):
    """
    optimized version of SI cascade generation

    g: the graph
    p: edge-wise infection probability
    min_fraction: useless parameter, to make interface consistent
    max_fraction: stopping if more than N x max_fraction nodes are infected
    """
    cdef float N = <float> g.num_vertices()
    cdef bool weighted = False, stop = False
    cdef int time = 0
    cdef int i, j

    # cdef infected
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

    edges = []

    if weighted:
        edge_weight_by_index = np.array(p.ma)

    infected_nodes_until_t = copy(infected)

    while len(infected) < N:
        infected_nodes_until_t = copy(infected)
        # print('current cascade size: {}'.format(len(infected_nodes_until_t)))
        time += 1
        for i in infected_nodes_until_t:
            for _, j, edge_index in g.get_out_edges(i):
                # only considers uninfected nodes
                if j not in infected:
                    if weighted:
                        inf_proba = edge_weight_by_index[edge_index]
                    else:
                        inf_proba = p

                    if random.random() <= inf_proba:
                        infected.add(j)
                        infection_times[j] = time
                        edges.append((i, j))

                        # stop when enough nodes have been infected
                        if (len(infected) / N) >= max_fraction:
                            stop = True
                            break
            if stop:
                break
        # print('loop done')
        if stop:
            break

    tree = Graph(directed=True)
    tree.add_vertex(g.num_vertices())
    tree.add_edge_list(edges)

    return source, infection_times, tree