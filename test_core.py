import pytest
import numpy as np
from core import uncertainty_scores
from fixture import g, obs


def test_uncertainty_scores(g, obs):
    scores = uncertainty_scores(g, obs, num_spt=10, num_stt=5, method='count')
    
    with pytest.raises(KeyError):
        for o in obs:
            scores[o]
    remain_nodes = set(np.arange(g.num_vertices())) - set(obs)
    for u in remain_nodes:
        assert scores[u] >= 0
