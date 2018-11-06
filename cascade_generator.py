import random
import math
import numpy as np
import pickle as pkl

from graph_tool import GraphView, PropertyMap
from graph_tool.topology import shortest_distance
from graph_tool.search import bfs_search

from tqdm import tqdm

from helpers import infected_nodes, sampling_weights_by_order
from graph_helpers import BFSNodeCollector, reverse_bfs
from si import si_opt as si
from ic import ic_opt

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
        return vis.nodes_in_order[:num_obs]  # head
    elif method == 'bfs-tail':
        assert tree is not None, 'the cascade tree is required'
        vis = BFSNodeCollector()
        bfs_search(GraphView(tree, directed=False), source, vis)
        return vis.nodes_in_order[-num_obs:]  # tail
    else:
        raise ValueError('unknown method {}'.format(method))


def ic(g, p, source=None, infected=None, min_fraction=0.0, max_fraction=0.5):
    """
    IC cascade generator that filters out small cascades (under min_fraction)
    """
    N = g.num_vertices()
    while True:
        source, times, tree = ic_opt(
            g, p=p,
            source=source,
            infected=infected,
            max_fraction=max_fraction
        )
        if (len(infected_nodes(times)) / N) >= min_fraction:
            break

    return source, times, tree


def gen_input(
        g,
        source=None,
        cascade_path=None,
        p=0.5,
        q=0.1,
        model='si',
        observation_method='uniform',
        min_fraction=0.0,
        max_fraction=1.0,
        return_tree=False
):
    if cascade_path is None:
        if model == 'si':
            s, c, tree = si(
                g, p,
                source=source,
                max_fraction=max_fraction
            )
        elif model == 'ic':
            s, c, tree = ic(
                g, p,
                source=source,
                min_fraction=min_fraction,
                max_fraction=max_fraction
            )
        else:
            raise ValueError('unknown cascade model')
    else:
        print('load from cache')
        c = pkl.load(open(cascade_path, 'rb'))
        s = np.nonzero([c == 0])[1][0]

    obs = observe_cascade(c, s, q, observation_method, tree=tree)

    if not return_tree:
        return obs, c, None
    else:
        return obs, c, tree
