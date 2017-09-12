import numpy as np
import pytest
from graph_tool.generation import lattice

from query_selection import QueryGenerator


def test_main():
    g = lattice((10, 10))
    obs = np.random.choice(np.arange(g.num_vertices()), 10, replace=False)

    q_gen = QueryGenerator(g, obs)
    qs = set()
    for i in range(g.num_vertices() - len(obs)):
        qs.add(q_gen.random())

    assert len(qs) == (g.num_vertices() - len(obs))
    assert (qs | set(obs)) == set(np.arange(g.num_vertices()))

    with pytest.raises(AssertionError):
        q_gen.random()
