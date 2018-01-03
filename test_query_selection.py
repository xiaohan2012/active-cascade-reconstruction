import pytest
from query_selection import (RandomQueryGenerator, EntropyQueryGenerator,
                             PRQueryGenerator, PredictionErrorQueryGenerator)
from simulator import Simulator
from graph_helpers import remove_filters, has_vertex
from fixture import g
from sample_pool import TreeSamplePool
from random_steiner_tree.util import from_gt


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


@pytest.mark.parametrize("query_method", ['random', 'pagerank', 'entropy', 'error'])
@pytest.mark.parametrize("sampling_method", ['cut_naive', 'cut', 'loop_erased'])
def test_query_method(g, query_method, sampling_method):
    print('query_method: ', query_method)
    print('sampling_method: ', sampling_method)

    gv = remove_filters(g)

    if query_method in {'entropy', 'error'}:
        gi = from_gt(g)
    else:
        gi = None

    pool = TreeSamplePool(gv,
                          n_samples=20,
                          method=sampling_method,
                          gi=gi,
                          return_tree_nodes=True  # using tree nodes
    )  
    if query_method == 'random':
        q_gen = RandomQueryGenerator(gv)
    elif query_method == 'pagerank':
        q_gen = PRQueryGenerator(gv)
    elif query_method == 'entropy':
        q_gen = EntropyQueryGenerator(gv, pool)
    elif query_method == 'error':
        q_gen = PredictionErrorQueryGenerator(gv, pool)

    sim = Simulator(gv, q_gen, gi=gi, print_log=True)
    print('simulator created')
    n_queries = 10
    qs, aux = sim.run(n_queries)
    print('sim.run finished')
    
    assert len(qs) == n_queries
    assert set(qs).intersection(set(aux['obs'])) == set()

    if query_method in {'entropy', 'error'}:
        check_tree_samples(qs, aux['c'], q_gen.sampler.samples)


# def est_entropy_method(g):
#     gv = remove_filters(g)
#     pool = TreeSamplePool(gv, n_samples=20)
#     q_gen = EntropyQueryGenerator(gv, pool)
#     sim = Simulator(gv, q_gen)
#     n_queries = 10
#     qs, aux = sim.run(n_queries)
    
#     assert len(qs) == n_queries
#     assert set(qs).intersection(set(aux['obs'])) == set()
#     check_tree_samples(qs, aux['c'], q_gen.sampler.tree_samples)


# def est_random(g):
#     gv = remove_filters(g)
#     q_gen = RandomQueryGenerator(gv)
#     sim = Simulator(gv, q_gen)
#     n_queries = 10
#     qs, aux = sim.run(n_queries)

#     assert len(qs) == n_queries
#     assert set(qs).intersection(set(aux['obs'])) == set()

# def est_pagerank(g):
#     gv = remove_filters(g)
#     q_gen = PRQueryGenerator(gv)
#     sim = Simulator(gv, q_gen)
#     n_queries = 10
#     qs, aux = sim.run(n_queries)

#     assert len(qs) == n_queries
#     assert set(qs).intersection(set(aux['obs'])) == set()
