import pytest
import numpy as np
import math
from infer_from_queries import infer_probas_from_queries
from fixture import g
from cascade_generator import gen_input
from graph_helpers import get_edge_weights
from test_helpers import check_tree_samples, check_error_esitmator, check_samples_so_far
from helpers import cascade_source


@pytest.mark.parametrize("cid", range(3))
@pytest.mark.parametrize("sampling_method", ['cut', 'loop_erased', 'simulation'])
@pytest.mark.parametrize("root_sampler_name", ['pagerank', 'true_root'])
def test_infer_probas_for_queries_sampling_approach(
        g, cid, sampling_method, root_sampler_name
):
    p = 0.5
    max_fraction = 0.5
    model = 'si'
    
    n_queries = 10

    obs, c, _ = gen_input(g, model=model, p=p, max_fraction=max_fraction)
    source = cascade_source(c)

    remaining_nodes = list(set(np.arange(g.num_vertices())) - set(obs))
    queries = np.random.permutation(remaining_nodes)[:n_queries]

    if sampling_method == 'simulation':
        n_samples = 10
        sampler_kwargs = dict(
            p=p,
            max_fraction=max_fraction,
            source=source,
            cascade_model=model,
            debug=True,
        )
    else:
        n_samples = 100
        sampler_kwargs = dict()

    inf_proba_list, sampler, estimator = infer_probas_from_queries(
        g, obs, c, queries,
        sampling_method,
        root_sampler_name=root_sampler_name,
        n_samples=n_samples,
        sampler_kwargs=sampler_kwargs
    )

    assert len(inf_proba_list) == n_queries + 1
    for i, probas in enumerate(inf_proba_list):
        print("iteration", i)
        assert probas.shape == (g.num_vertices(), )

        for o in obs:
            assert probas[o] == 1.0

        for q in queries[:i]:  # previous i-1 queries
            if c[q] == -1:
                assert probas[q] == 0.0
            else:
                assert probas[q] == 1.0

    check_tree_samples(queries, c, sampler.samples)
    check_error_esitmator(queries, c, estimator)


@pytest.mark.parametrize("rep", range(3))
@pytest.mark.parametrize("every", [1, 2, 4, 8])
def test_every(g, rep, every):
    n_queries = 20
    p = get_edge_weights(g)
    obs, c, _ = gen_input(g, model='si', p=p, q=0.2)
    remaining_nodes = list(set(np.arange(g.num_vertices())) - set(obs))
    queries = np.random.permutation(remaining_nodes)[:n_queries]

    inf_proba_list, sampler, estimator = infer_probas_from_queries(
        g, obs, c, queries,
        'loop_erased', root_sampler_name='true_root', n_samples=100,
        iter_callback=check_samples_so_far,
        every=every)

    assert len(inf_proba_list) == (math.ceil(n_queries / every) + 1)
    for i, probas in enumerate(inf_proba_list):
        print(i)
        assert probas.shape == (g.num_vertices(), )
        if i % every == 0:
            for o in obs:
                assert probas[o] == 1.0

            for q in queries[:i]:  # previous i-1 queries
                if c[q] == -1:
                    assert probas[q] == 0.0
                else:
                    assert probas[q] == 1.0

    check_tree_samples(queries, c, sampler.samples, every)
    check_error_esitmator(queries, c, estimator, every)
