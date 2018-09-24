from minimum_steiner_tree import min_steiner_tree


def infection_probability(g, obs, sampler, error_estimator):
    """
    infer infection probability over nodes given `obs` and using `sampler`
    """
    if error_estimator._m is None:
        error_estimator.build_matrix(sampler.samples)
    
    return error_estimator.unconditional_proba()
