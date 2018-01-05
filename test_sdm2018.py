import numpy as np
import pytest
from graph_tool.generation import lattice

from sdm2018 import find_tree_greedy

from sdm2018.utils import earliest_obs_node
from sdm2018.feasibility import is_feasible
from sdm2018.cascade import gen_nontrivial_cascade


QS = np.linspace(0.1, 1.0, 10)
MODELS = ['si', 'ct']

P = 0.5
K = 10


@pytest.fixture
def cascades_on_grid():
    cascades = []
    g = lattice((8, 8))
    for model in MODELS:
        for q in QS:
            for i in range(K):
                ret = gen_nontrivial_cascade(
                    g, P, q, model=model, return_tree=True,
                    source_includable=True)
                ret = (g, ) + ret + (model, q, i)
                cascades.append(ret)  # g, infection_times, source, obs_nodes, true_tree
    return cascades
        

def test_greedy(cascades_on_grid):
    for g, infection_times, source, obs_nodes, true_tree, model, q, i in cascades_on_grid:
        print(model, q, i)
        root = earliest_obs_node(obs_nodes, infection_times)
        tree = find_tree_greedy(
            g, root, infection_times, source, obs_nodes,
            debug=False,
            verbose=True
        )
        assert is_feasible(tree, root, obs_nodes, infection_times)
