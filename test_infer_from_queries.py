import pytest
import numpy as np
from infer_from_queries import (infer_probas_from_queries)
from fixture import g
from experiment import gen_input
from test_helpers import check_tree_samples, check_error_esitmator


@pytest.mark.parametrize("cid", range(5))
@pytest.mark.parametrize("sampling_method", ['cut', 'loop_erased'])
@pytest.mark.parametrize("root_sampler_name", ['random', 'pagerank', 'true_root'])
def test_infer_probas_for_queries_sampling_approach(g, cid, sampling_method, root_sampler_name):
    n_queries = 20
    obs, c = gen_input(g, model='ic')
    remaining_nodes = list(set(np.arange(g.num_vertices())) - set(obs))
    queries = np.random.permutation(remaining_nodes)[:n_queries]

    inf_proba_list, sampler, estimator = infer_probas_from_queries(
        g, obs, c, queries,
        sampling_method, root_sampler_name=root_sampler_name, n_samples=100)

    assert len(inf_proba_list) == n_queries + 1
    for i, probas in enumerate(inf_proba_list):
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


