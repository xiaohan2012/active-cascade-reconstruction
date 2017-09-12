import numpy as np
import pytest
from graph_tool.generation import lattice


@pytest.fixture
def g():
    return lattice((10, 10))


@pytest.fixture
def obs(g):
    return np.random.choice(np.arange(g.num_vertices()), 10, replace=False)

