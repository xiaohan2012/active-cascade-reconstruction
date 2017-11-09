from query_selection import (RandomQueryGenerator, EntropyQueryGenerator,
                             PRQueryGenerator, PredictionErrorQueryGenerator)
from simulator import Simulator
from graph_helpers import remove_filters
from fixture import g


def test_error_based_method(g):
    gv = remove_filters(g)
    q_gen = PredictionErrorQueryGenerator(gv, num_stt=20)
    sim = Simulator(gv, q_gen)
    n_queries = 10
    qs, aux = sim.run(n_queries)
    
    assert len(qs) == n_queries
    assert set(qs).intersection(set(aux['obs'])) == set()


def test_entropy_method(g):
    gv = remove_filters(g)
    q_gen = EntropyQueryGenerator(gv, num_stt=20)
    sim = Simulator(gv, q_gen)
    n_queries = 10
    qs, aux = sim.run(n_queries)
    
    assert len(qs) == n_queries
    assert set(qs).intersection(set(aux['obs'])) == set()
        

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
