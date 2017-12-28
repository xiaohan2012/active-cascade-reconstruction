from query_selection import (RandomQueryGenerator, EntropyQueryGenerator,
                             PRQueryGenerator, PredictionErrorQueryGenerator)
from simulator import Simulator
from graph_helpers import remove_filters, has_vertex
from fixture import g
from sample_pool import TreeSamplePool



def check_tree_samples(qs, c, trees):
    # make sure the tree sampels are updated
    for q in qs:
        for t in trees:
            if c[q] >= 0:
                if isinstance(t, set):
                    assert q in t
                else:
                    assert has_vertex(t, q)
            else:
                if isinstance(t, set):
                    assert q not in t
                else:
                    assert not has_vertex(t, q)


def test_error_based_method(g):
    gv = remove_filters(g)
    pool = TreeSamplePool(gv, n_samples=20)
    q_gen = PredictionErrorQueryGenerator(gv, pool)
    sim = Simulator(gv, q_gen)
    n_queries = 10
    qs, aux = sim.run(n_queries)
    
    assert len(qs) == n_queries
    assert set(qs).intersection(set(aux['obs'])) == set()

    check_tree_samples(qs, aux['c'], q_gen.tree_pool.nodes_samples)


def test_entropy_method(g):
    gv = remove_filters(g)
    pool = TreeSamplePool(gv, n_samples=20)
    q_gen = EntropyQueryGenerator(gv, pool)
    sim = Simulator(gv, q_gen)
    n_queries = 10
    qs, aux = sim.run(n_queries)
    
    assert len(qs) == n_queries
    assert set(qs).intersection(set(aux['obs'])) == set()
    check_tree_samples(qs, aux['c'], q_gen.tree_pool.tree_samples)


def test_random(g):
    gv = remove_filters(g)
    q_gen = RandomQueryGenerator(gv)
    sim = Simulator(gv, q_gen)
    n_queries = 10
    qs, aux = sim.run(n_queries)

    assert len(qs) == n_queries
    assert set(qs).intersection(set(aux['obs'])) == set()

def test_pagerank(g):
    gv = remove_filters(g)
    q_gen = PRQueryGenerator(gv)
    sim = Simulator(gv, q_gen)
    n_queries = 10
    qs, aux = sim.run(n_queries)

    assert len(qs) == n_queries
    assert set(qs).intersection(set(aux['obs'])) == set()
