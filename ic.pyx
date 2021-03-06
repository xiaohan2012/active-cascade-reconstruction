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

from exceptions import TooManyInfections
from helpers import raise_if_not_iterable

# C++ stuff
from libcpp cimport bool
from libcpp.set cimport set as cppset
from libcpp.pair cimport pair


cpdef ic_opt(g, p, source=None, infected=None, float max_fraction=0.5, int verbose=False):
    """
    optimized version of IC cascade generation

    g: the graph
    p: edge-wise infection probability
    max_fraction: stopping if more than N x max_fraction nodes are infected
    """
    cdef float N = <float> g.num_vertices()
    cdef bool weighted = False, stop = False
    cdef int time = 0
    cdef int i, j
    cdef cppset[pair[int, int]] attempted_edges;

    active_degree = g.degree_property_map('out').a
    # cdef infected
    if isinstance(p, PropertyMap):
        weighted = True
    else:
        # is float and uniform
        assert 0 < p and p <= 1

    if source is None and infected is None:
        source = random.choice(np.arange(g.num_vertices()))

    if infected is None:
        infected = {source}
    else:
        raise_if_not_iterable(infected)
        infected = set(infected)
        # check size
        cascade_fraction = len(infected) / g.num_vertices()
        if cascade_fraction > max_fraction:
            raise TooManyInfections

    infection_times = np.ones(g.num_vertices()) * -1
    infection_times[list(infected)] = 0

    edges = []

    if weighted:
        edge_weight_by_index = np.array(p.ma)

    frontier_pool = copy(infected)
    max_num_infections = int(max_fraction * N)

    while len(infected) < max_num_infections and len(frontier_pool) > 0:
        # print('current cascade size: {}'.format(len(frontier_pool)))
        time += 1
        if verbose >= 1:
            print('at time ', time)
            print('frontier_pool', frontier_pool)
            print('active_degree', active_degree)

        frontiers_to_remove = set()
        frontiers_to_add = set()
        for i in frontier_pool:
            for _, j, edge_index in g.get_out_edges(i):
                if verbose >= 2:
                    print('trying ', (i, j))

                # if the edge has not be attempted before
                if attempted_edges.find((i, j)) == attempted_edges.end():
                    if verbose >= 2:
                        print('go into ', (i, j))
                    active_degree[i] -= 1
                    if active_degree[i] == 0:
                        # no more out edges to go
                        if verbose >= 2:
                            print('remove {} from pool'.format(i))
                        frontiers_to_remove.add(i)

                    attempted_edges.insert((i, j))

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

                            if verbose >= 1:
                                print('add {} to frontier'.format(j))

                            frontiers_to_add.add(j)
                            # stop when enough nodes have been infected
                            if (len(infected) / N) >= max_fraction:
                                stop = True
                                break
            if stop:
                break
        frontier_pool -= frontiers_to_remove
        frontier_pool |= frontiers_to_add
        if stop:
            break

    tree = Graph(directed=True)
    tree.add_vertex(g.num_vertices())
    tree.add_edge_list(edges)

    return source, infection_times, tree
