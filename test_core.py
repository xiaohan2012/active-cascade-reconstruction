import pytest
import numpy as np
from random_steiner_tree import util

from core import uncertainty_scores, sample_steiner_trees
from graph_helpers import is_steiner_tree
from fixture import g, obs


@pytest.fixture
def gi(g):
    return util.from_gt(g, None)


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
        

@pytest.mark.parametrize("return_tree_nodes", [True, False])
@pytest.mark.parametrize("method", ['cut_naive', 'cut', 'loop_erased'])
def test_sample_steiner_trees(g, gi, obs, return_tree_nodes, method):
    n_samples = 100
    st_trees_all = sample_steiner_trees(g, obs, method, n_samples,
                                        gi=gi,
                                        return_tree_nodes=return_tree_nodes)
    assert len(st_trees_all) == n_samples

    for t in st_trees_all:
        if return_tree_nodes:
            assert set(obs).issubset(t)
        else:
            assert is_steiner_tree(t, obs)
