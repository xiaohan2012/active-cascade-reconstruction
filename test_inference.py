import numpy as np
from inference import infer_infected_nodes, infection_probability
from graph_helpers import (gen_random_spanning_tree, extract_nodes,
                           remove_filters,
                           observe_uninfected_node)
from random_steiner_tree.util import isolate_vertex
from core import sample_steiner_trees
from sample_pool import TreeSamplePool
from fixture import g, gi, obs


def test_inf_probas_shape(g, gi, obs):
    sampler = TreeSamplePool(g, 25, 'cut', gi=gi,
                             return_tree_nodes=True)
    g = remove_filters(g)
    n = g.num_vertices()
    all_nodes = extract_nodes(g)
    remaining_nodes = list(set(all_nodes) - set(obs))

    # first round
    removed = remaining_nodes[0]

    observe_uninfected_node(g, removed, obs)
    isolate_vertex(gi, removed)
    
    probas = infection_probability(g, obs, sampler)
    assert probas.shape == (n,)
    assert probas[removed] == 0
    for o in obs:
        assert probas[o] == 1.0

    # second tround
    removed = remaining_nodes[1]

    observe_uninfected_node(g, removed, obs)
    isolate_vertex(gi, removed)
        
    probas = infection_probability(g, obs, sampler)
    assert probas.shape == (n,)
    assert probas[removed] == 0
    for o in obs:
        assert probas[o] == 1.0
        

def test_infer_infected_nodes_sampling_approach(g, gi, obs):
    sampler = TreeSamplePool(g, 100, 'cut', gi=gi,
                             return_tree_nodes=True)
    g = remove_filters(g)

    # with min steiner trees
    inf_nodes = infer_infected_nodes(g, obs, sampler=None, use_proba=False, method="min_steiner_tree")
    # simple test, just make sure observation is in the prediction
    assert set(obs).issubset(set(inf_nodes))

    # sampling approach without probability
    inf_nodes2 = infer_infected_nodes(g, obs, sampler, use_proba=False, method="sampling")
    assert set(obs).issubset(set(inf_nodes2))

    # sampling approach with probability
    probas = infer_infected_nodes(g, obs, sampler, use_proba=True, method="sampling")

    assert isinstance(probas, np.ndarray)
    assert probas.dtype == np.float
    
