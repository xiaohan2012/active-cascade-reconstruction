import numpy as np
import pytest
from query_selection import RandomQueryGenerator, EntropyQueryGenerator, PRQueryGenerator
from simulator import Simulator
from graph_helpers import remove_filters
from fixture import g, obs


def test_random(g, obs):
    q_gen = RandomQueryGenerator(g, obs)
    qs = set()
    for i in range(g.num_vertices() - len(obs)):
        qs.add(q_gen.select_query())

    assert len(qs) == (g.num_vertices() - len(obs))
    assert (qs | set(obs)) == set(np.arange(g.num_vertices()))

    with pytest.raises(AssertionError):
        q_gen.select_query()


def test_entropy_method(g):
    gv = remove_filters(g)
    q_gen = EntropyQueryGenerator(gv, obs, num_stt=20)
    sim = Simulator(gv, q_gen)
    n_queries = 10
    qs, aux = sim.run(n_queries)
    
    assert len(qs) == n_queries
    if aux['graph_changed']:
        assert gv.num_vertices() < g.num_vertices
        assert gv.num_edges() < g.num_edges()
    else:
        assert gv.num_vertices() == g.num_vertices
        assert gv.num_edges() == g.num_edges()


def test_pagerank(g, obs):
    q_gen = PRQueryGenerator(g, obs)
    qs = set()
    for i in range(g.num_vertices() - len(obs)):
        qs.add(q_gen.select_query())

    assert len(qs) == (g.num_vertices() - len(obs))
    assert (qs | set(obs)) == set(np.arange(g.num_vertices()))

    with pytest.raises(AssertionError):
        q_gen.select_query()
