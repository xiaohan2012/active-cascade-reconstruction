import pytest
from query_selection import (RandomQueryGenerator, EntropyQueryGenerator,
                             PRQueryGenerator, PredictionErrorQueryGenerator)
from simulator import Simulator
from graph_helpers import remove_filters, has_vertex
from fixture import g
from sample_pool import TreeSamplePool
from random_steiner_tree.util import from_gt
from tree_stat import TreeBasedStatistics


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


def check_error_esitmator(qs, c, est):
    # make sure the tree sampels are updated
    for q in qs:
        if c[q] >= 0:
            # infected
            assert est._m[q, :].sum() == est.n_col
        else:
            # uninfected
            assert est._m[q, :].sum() == 0


@pytest.mark.parametrize("query_method", ['random', 'pagerank', 'entropy', 'error'])
@pytest.mark.parametrize("sampling_method", ['cut_naive', 'cut', 'loop_erased'])
@pytest.mark.parametrize("root_sampler", [None, 'earliest_nbrs', 'earliest_obs'])
def test_query_method(g, query_method, sampling_method, root_sampler):
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
        error_estimator = TreeBasedStatistics(gv)
        q_gen = PredictionErrorQueryGenerator(gv, pool,
                                              error_estimator=error_estimator,
                                              prune_nodes=True,
                                              n_node_samples=10,
                                              root_sampler=root_sampler)

    sim = Simulator(gv, q_gen, gi=gi, print_log=True)
    print('simulator created')
    n_queries = 10
    qs, aux = sim.run(n_queries)
    print('sim.run finished')
    
    assert len(qs) == n_queries
    assert set(qs).intersection(set(aux['obs'])) == set()

    if query_method in {'entropy', 'error'}:
        check_tree_samples(qs, aux['c'], q_gen.sampler.samples)
    if query_method == 'error':
        # ensure that error estimator updates its tree samples
        check_error_esitmator(qs, aux['c'], error_estimator)
