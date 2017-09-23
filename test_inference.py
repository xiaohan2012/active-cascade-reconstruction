from inference import infer_infected_nodes
from graph_helpers import gen_random_spanning_tree
from core import sample_steiner_trees
from fixture import g, obs


def test_infer_infected_nodes_sampling_approach(g, obs):
    n_samples = 100
    sp_trees = [gen_random_spanning_tree(g) for _ in range(n_samples)]

    # with steiner trees
    st_trees = sample_steiner_trees(g, obs, n_samples, sp_trees=sp_trees)
    inf_nodes = infer_infected_nodes(g, obs, method="sampling", st_trees=st_trees)

    # simple test, just make sure observation is in the prediction
    assert set(obs).issubset(set(inf_nodes))

    # with spanning trees
    inf_nodes1 = infer_infected_nodes(g, obs, method="sampling", sp_trees=sp_trees)
    assert set(obs).issubset(set(inf_nodes1))
    assert set(inf_nodes1) == set(inf_nodes)
    
    # without anything
    inf_nodes2 = infer_infected_nodes(g, obs, method="sampling", n_samples=n_samples)
    assert set(obs).issubset(set(inf_nodes2))

    # take top-25 trees for inference
    inf_nodes3 = infer_infected_nodes(g, obs, method="sampling",
                                      subset_size=25,
                                      n_samples=n_samples)
    assert set(obs).issubset(set(inf_nodes3))
