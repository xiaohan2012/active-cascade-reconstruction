import pytest
import numpy as np
from core import uncertainty_scores, sample_steiner_trees
from graph_helpers import gen_random_spanning_tree
from fixture import g, obs


def test_uncertainty_scores(g, obs):
    ######## use SIR ############
    scores = uncertainty_scores(g, obs, num_spt=10, num_stt=5, method='count',
                                use_resample=True)
    
    with pytest.raises(KeyError):
        for o in obs:
            scores[o]
    remain_nodes = set(np.arange(g.num_vertices())) - set(obs)
    for u in remain_nodes:
        assert scores[u] >= 0


    ######## not use SIR ############
    scores = uncertainty_scores(g, obs, num_spt=10, num_stt=5,
                                method='count', use_resample=False)
    
    with pytest.raises(KeyError):
        for o in obs:
            scores[o]
    remain_nodes = set(np.arange(g.num_vertices())) - set(obs)
    for u in remain_nodes:
        assert scores[u] >= 0
        

def test_sample_steiner_trees(g, obs):
    n_samples = 100
    sp_trees = [gen_random_spanning_tree(g) for i in range(100)]
    st_trees_all = sample_steiner_trees(g, obs, n_samples, None, sp_trees=sp_trees)
    assert len(st_trees_all) == n_samples
    
    subset_size = 10
    st_trees = sample_steiner_trees(g, obs, n_samples, subset_size, sp_trees=sp_trees)
    assert len(st_trees) == subset_size

    # make sure order is correct
    min_size = st_trees[0].num_edges()
    for t in st_trees_all:
        assert min_size <= t.num_edges()
