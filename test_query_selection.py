import numpy as np
import pytest
from query_selection import RandomQueryGenerator, OurQueryGenerator, PRQueryGenerator
from graph_helpers import isolate_node, add_ve_filters
from experiment import gen_input
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


def test_our_method(g):
    # make sure it runnable
    obs, c = gen_input(g)
    gv = add_ve_filters(g)

    q_gen = OurQueryGenerator(gv, obs, num_spt=20, num_stt=5)
    qs = set()
    n_queries = 10

    inf_nodes = list(obs)
    for i in range(n_queries):
        q = q_gen.select_query(gv, inf_nodes)
        qs.add(q)
        if c[q] == -1:
            isolate_node(gv, q)
        else:
            inf_nodes.append(q)

    assert len(qs) == n_queries
    assert gv.num_edges() < g.num_edges()
    assert gv.num_vertices() == g.num_vertices()


def test_pagerank(g, obs):
    q_gen = PRQueryGenerator(g, obs)
    qs = set()
    for i in range(g.num_vertices() - len(obs)):
        qs.add(q_gen.select_query())

    assert len(qs) == (g.num_vertices() - len(obs))
    assert (qs | set(obs)) == set(np.arange(g.num_vertices()))

    with pytest.raises(AssertionError):
        q_gen.select_query()
