import pytest
import numpy as np
from query_selection import (
    RandomQueryGenerator,
    EntropyQueryGenerator,
    PRQueryGenerator,
    CondEntropyQueryGenerator,
    MutualInformationQueryGenerator,
    SamplingBasedGenerator,
    LatestFirstOracle,
    EarliestFirstOracle
)
from simulator import Simulator
from graph_helpers import remove_filters, get_edge_weights
from fixture import g, line
from sample_pool import (
    TreeSamplePool,
    SimulatedCascadePool
)
from random_steiner_tree.util import from_gt
from tree_stat import TreeBasedStatistics
from cascade_generator import si
from test_helpers import (
    check_tree_samples,
    check_error_esitmator,
    check_samples_so_far
)
from helpers import infected_nodes


def iter_callback(g, q_gen, *args):
    if isinstance(q_gen, SamplingBasedGenerator):
        check_samples_so_far(g, q_gen.sampler,
                             q_gen.error_estimator, *args)


@pytest.mark.parametrize("query_method", ['random', 'pagerank', 'entropy', 'cond_entropy', 'mutual-info'])
@pytest.mark.parametrize("sampling_method", ['loop_erased', 'cut'])
@pytest.mark.parametrize("root_sampler", ['true_root', 'random'])
def test_query_method(g, query_method, sampling_method, root_sampler):
    print('query_method: ', query_method)
    print('sampling_method: ', sampling_method)
    print('root_sampler: ', root_sampler)

    gv = remove_filters(g)
    print(gv.num_edges())
    edge_weights = get_edge_weights(gv)

    if query_method in {'entropy', 'cond_entropy', 'mutual-info'}:
        gi = from_gt(g, edge_weights)
    else:
        gi = None

    pool = TreeSamplePool(
        gv,
        n_samples=20,
        method=sampling_method,
        gi=gi,
        return_type='nodes',  # using tree nodes
    )

    error_estimator = TreeBasedStatistics(gv)

    if query_method == 'random':
        q_gen = RandomQueryGenerator(gv)
    elif query_method == 'pagerank':
        q_gen = PRQueryGenerator(gv)
    elif query_method == 'entropy':
        q_gen = EntropyQueryGenerator(gv, pool,
                                      error_estimator=error_estimator,
                                      root_sampler=root_sampler)
    elif query_method == 'cond_entropy':
        q_gen = CondEntropyQueryGenerator(gv, pool,
                                              error_estimator=error_estimator,
                                              prune_nodes=True,
                                              n_node_samples=None,
                                              root_sampler=root_sampler)
    elif query_method == 'mutual-info':
        q_gen = MutualInformationQueryGenerator(
            gv, pool,
            error_estimator=error_estimator,
            prune_nodes=True,
            n_node_samples=None,
            root_sampler=root_sampler)

    sim = Simulator(gv, q_gen, gi=gi, print_log=True)
    print('simulator created')
    n_queries = 10
    qs, aux = sim.run(n_queries,
                      gen_input_kwargs={'min_fraction': 20. / gv.num_vertices()},
                      iter_callback=iter_callback)
    print('sim.run finished')

    assert len(qs) == n_queries
    assert set(qs).intersection(set(aux['obs'])) == set()

    if query_method in {'entropy', 'cond_entropy'}:
        check_tree_samples(qs, aux['c'], q_gen.sampler.samples)

    if query_method in {'cond_entropy'}:
        # ensure that error estimator updates its tree samples
        check_error_esitmator(qs, aux['c'], error_estimator)


@pytest.mark.parametrize("query_method", ['entropy'])
def test_under_simulated_cascade(g, query_method):
    n_obs = 5
    n_samples = 20
    n_queries = 5
    
    print('query_method: ', query_method)

    gv = remove_filters(g)
    print(gv.num_edges())

    cascade_params = dict(
        p=0.5,
        max_fraction=0.5,
        verbose=2
    )
    source, times, _ = si(
        g, source=None,
        p=cascade_params['p'],
        max_fraction=cascade_params['max_fraction']
    )
    cascade_params['source'] = source

    inf_nodes = infected_nodes(times)
    obs = set(np.random.choice(inf_nodes, n_obs, replace=False))

    pool = SimulatedCascadePool(
        gv,
        n_samples,
        cascade_model='si',
        approach='mst',
        cascade_params=cascade_params
    )

    error_estimator = TreeBasedStatistics(gv)

    if query_method == 'entropy':
        q_gen = EntropyQueryGenerator(gv, pool,
                                      error_estimator=error_estimator,
                                      root_sampler='random')
    elif query_method == 'cond_entropy':
        q_gen = CondEntropyQueryGenerator(gv, pool,
                                              error_estimator=error_estimator,
                                              prune_nodes=True,
                                              n_node_samples=None,
                                              root_sampler='random')
    else:
        raise ValueError

    sim = Simulator(gv, q_gen, print_log=True)

    qs, aux = sim.run(
        n_queries,
        c=times,
        obs=obs
    )
    print('sim.run finished')

    assert len(qs) == n_queries
    assert set(qs).intersection(set(aux['obs'])) == set()

    if query_method in {'entropy', 'cond_entropy'}:
        check_tree_samples(qs, times, pool.samples)

    if query_method in {'cond_entropy'}:
        # ensure that error estimator updates its tree samples
        check_error_esitmator(qs, times, error_estimator)
        
        
def test_no_more_query(g):
    gv = remove_filters(g)

    q_gen = RandomQueryGenerator(gv)
    sim = Simulator(gv, q_gen, print_log=True)

    qs, aux = sim.run(g.num_vertices()+100)
    assert len(qs) < g.num_vertices()


def build_simulator_using_cond_entropy_query_selector(g, **kwargs):
    gv = remove_filters(g)
    gi = from_gt(g)
    pool = TreeSamplePool(
        gv,
        n_samples=1000,
        method='loop_erased',
        gi=gi,
        return_type='nodes'  # using tree nodes
    )

    q_gen = CondEntropyQueryGenerator(
        gv, pool,
        error_estimator=TreeBasedStatistics(gv),
        root_sampler='random',
        **kwargs
    )
    
    return Simulator(gv, q_gen, gi=gi, print_log=True), q_gen


@pytest.mark.parametrize("repeat_id", range(5))
def test_cond_entropy_with_candidate_pruning(g, repeat_id):
    min_probas = [0, 0.1, 0.2, 0.3, 0.4]
    cand_nums = []

    for min_proba in min_probas:
        sim, q_gen = build_simulator_using_cond_entropy_query_selector(
            g, prune_nodes=True, min_proba=min_proba
        )

        sim.run(0, force_receive_obs=True)  # just get the candidates
        q_gen.prune_candidates()  # and prune the candidates

        cand_nums.append(len(q_gen._cand_pool))

    # number of candidates should be decreasing (more accurately, non-increasing)
    for prev, cur in zip(cand_nums, cand_nums[1:]):
        assert prev >= cur


def test_cond_entropy_sample_nodes_for_estimation(g):
    n_node_samples_list = [10, 20, 30, 40, 50]
    for n_node_samples in n_node_samples_list:
        sim, q_gen = build_simulator_using_cond_entropy_query_selector(
            g, n_node_samples=n_node_samples
        )
        sim.run(0, force_receive_obs=True)

        samples = q_gen._sample_nodes_for_estimation()
        assert len(samples) == n_node_samples
