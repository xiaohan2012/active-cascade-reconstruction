import pytest

from sample_pool import TreeSamplePool
from fixture import g, gi, obs

N_SAMPLES = 1000

@pytest.mark.parametrize('return_type', ['nodes', 'tuples'])
def test_resampling(g, gi, obs, return_type):
    pool = TreeSamplePool(g, gi=gi,
                          n_samples=N_SAMPLES,
                          method='loop_erased',
                          with_inc_sampling=False,
                          with_resampling=True,
                          return_type=return_type)
    pool.fill(obs)

    if return_type == 'tuples':
        # type checking
        for t in pool.samples:
            assert isinstance(t, tuple)
            for e in t:
                assert isinstance(e, tuple)
                assert len(e) == 2
        unique_resampled_trees = set(pool.samples)
        
    elif return_type == 'nodes':
        for t in pool.samples:
            assert isinstance(t, set)
        unique_resampled_trees = set(map(tuple, pool.samples))
        
    unique_sampled_trees = set(pool._old_samples)
    
    print(len(unique_resampled_trees))
    assert len(unique_resampled_trees) < 10  # far few unique resampled trees
    assert len(unique_sampled_trees) == N_SAMPLES  # with high probability

    
