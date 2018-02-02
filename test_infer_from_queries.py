import pytest
import numpy as np
from infer_from_queries import (infer_probas_from_queries)
from fixture import g
from experiment import gen_input
from test_helpers import check_tree_samples, check_error_esitmator


@pytest.mark.parametrize("cid", range(10))
@pytest.mark.parametrize("sampling_method", ['cut', 'loop_erased'])
@pytest.mark.parametrize("root_sampler_name", [None, 'pagerank'])
def test_infer_probas_for_queries_sampling_approach(g, cid, sampling_method, root_sampler_name):
    n_queries = 20
    obs, c = gen_input(g)
    remaining_nodes = list(set(np.arange(g.num_vertices())) - set(obs))
    queries = np.random.permutation(remaining_nodes)[:n_queries]

    inf_proba_list, sampler, estimator = infer_probas_from_queries(
        g, obs, c, queries,
        sampling_method, root_sampler_name=root_sampler_name, n_samples=100)

    assert len(inf_proba_list) == n_queries
    for probas in inf_proba_list:
        assert probas.shape == (g.num_vertices(), )

    check_tree_samples(queries, c, sampler.samples)
    check_error_esitmator(queries, c, estimator)


