import numpy as np
from inference import infer_infected_nodes, infection_probability
from graph_helpers import (gen_random_spanning_tree, extract_nodes,
                           remove_filters,
                           observe_uninfected_node)
from core import sample_steiner_trees
from fixture import g, obs


def test_inf_probas_shape(g, obs):
    g = remove_filters(g)
    n = g.num_vertices()
    all_nodes = extract_nodes(g)
    remaining_nodes = list(set(all_nodes) - set(obs))

    # first round
    removed = remaining_nodes[0]

    observe_uninfected_node(g, removed, obs)
    
    probas = infection_probability(g, obs, n_samples=10)
    assert probas.shape == (n,)
    assert probas[removed] == 0
    for o in obs:
        assert probas[o] == 1.0

    # second tround
    removed = remaining_nodes[1]

    observe_uninfected_node(g, removed, obs)
    
    probas = infection_probability(g, obs, n_samples=100)
    assert probas.shape == (n,)
    assert probas[removed] == 0
    for o in obs:
        assert probas[o] == 1.0
        

def test_infer_infected_nodes_sampling_approach(g, obs):
    g = remove_filters(g)
    n_samples = 100
    sp_trees = [gen_random_spanning_tree(g) for _ in range(n_samples)]

    # with steiner trees
    st_trees = sample_steiner_trees(g, obs, n_samples, sp_trees=sp_trees)
    inf_nodes = infer_infected_nodes(g, obs, use_proba=False, method="sampling", st_trees=st_trees)

    # simple test, just make sure observation is in the prediction
    assert set(obs).issubset(set(inf_nodes))

    # with spanning trees
    inf_nodes1 = infer_infected_nodes(g, obs, use_proba=False, method="sampling", sp_trees=sp_trees)
    assert set(obs).issubset(set(inf_nodes1))
    assert set(inf_nodes1) == set(inf_nodes)
    
    # without anything
    inf_nodes2 = infer_infected_nodes(g, obs, use_proba=False, method="sampling", n_samples=n_samples)
    assert set(obs).issubset(set(inf_nodes2))

    # take top-25 trees for inference
    inf_nodes3 = infer_infected_nodes(g, obs, use_proba=False,
                                      method="sampling",
                                      subset_size=25,
                                      n_samples=n_samples)
    assert set(obs).issubset(set(inf_nodes3))

    # test_with_proba
    st_trees = sample_steiner_trees(g, obs, n_samples, sp_trees=sp_trees)
    probas = infer_infected_nodes(g, obs, use_proba=True, method="sampling", st_trees=st_trees)

    assert isinstance(probas, np.ndarray)
    assert probas.dtype == np.float
    
