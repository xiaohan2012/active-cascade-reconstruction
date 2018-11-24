import random
from scipy.stats import entropy
from tqdm import tqdm

from graph_helpers import (
    extract_nodes,
    extract_steiner_tree,
    gen_random_spanning_tree,
    filter_graph_by_edges,
    reachable_node_set,
    swap_end_points
)
from inference import infection_probability
from helpers import infected_nodes

from random_steiner_tree import random_steiner_tree
from random_steiner_tree.util import from_gt

from cascade_generator import si, ic
from exceptions import TooManyInfections

from joblib import (delayed, Parallel)
from minimum_steiner_tree import min_steiner_tree

SIMULATION_METHODS = ('naive', 'mst', 'rst', 'rrs')

def uncertainty_scores(
        g, obs,
        sampler,
        error_estimator
):
    """
    calculate uncertainty scores based on sampled steiner trees

    Args:

    Graph `g`
    list of int `obs`: list of observed nodes
    sampler: the tree sampler
    error_estimator: what does the actual counting
    str `method`: {'count', 'entropy'}

    Returns:

    dict of (int, float): node to uncertainty score
    """
    if sampler.is_empty:
        sampler.fill(obs)

    p = infection_probability(g, obs, sampler, error_estimator)
    non_obs_nodes = set(extract_nodes(g)) - set(obs)

    uncert = [entropy([v, 1-v]) for v in p]

    r = {n: uncert[n]
         for n in non_obs_nodes}
    return r


def sample_steiner_trees(g, obs,
                         method,
                         n_samples,
                         gi=None,
                         root=None,
                         root_sampler=None,
                         return_type='nodes',
                         log=False,
                         verbose=False):
    """sample `n_samples` steiner trees that span `obs` in `g`

    `method`: the method for sampling steiner tree
    `n_samples`: sample size
    `gi`: the Graph object that is used if `method` in {'cut', 'loop_erased'}
    `root_sampler`: function that samples a root
    `return_type`: if True, return the set of nodes that are in the sampled steiner tree
    """
    assert method in {'cut', 'cut_naive', 'loop_erased'}

    steiner_tree_samples = []
    # for i in tqdm(range(n_samples), total=n_samples):
    if log:
        iters = tqdm(range(n_samples), total=n_samples)
    else:
        iters = range(n_samples)

    for i in iters:
        if root is None:
            # if root not give, sample it using some sampler
            if root_sampler is None:
                # print('random root')
                # note: isolated nodes are ignored
                node_set = reachable_node_set(g, list(obs)[0])
                r = int(random.choice(list(node_set)))
            else:
                # print('custom root sampler')
                assert callable(root_sampler), 'root_sampler should be callable'
                # print('root_sampler', root_sampler)
                r = root_sampler()
                # print('root', r)
        else:
            r = root

        if method == 'cut_naive':
            rand_t = gen_random_spanning_tree(g, root=r)
            st = extract_steiner_tree(rand_t, obs, return_nodes=return_type)
            # if return_type:
            #     st = set(map(int, st.vertices()))
        elif method in {'cut', 'loop_erased'}:
            assert gi is not None
            # print('der')
            edges = random_steiner_tree(gi, obs, r, method, verbose=verbose)
            if return_type == 'nodes':
                st = set(u for e in edges for u in e)
            elif return_type == 'tuples':
                st = swap_end_points(edges)
            elif return_type == 'tree':
                st = filter_graph_by_edges(g, edges)
            else:
                raise ValueError('unknown return_type {}'.format(return_type))

        steiner_tree_samples.append(st)

    return steiner_tree_samples


def sample_one_by_simulation(g, obs, cascade_model, **kwargs):
    if cascade_model == 'si':
        assert 'p' in kwargs
        assert 'source' in kwargs
        assert 'max_fraction' in kwargs
        func = lambda: si(g, **kwargs)
    elif cascade_model == 'ic':
        assert 'p' in kwargs
        assert 'source' in kwargs
        assert 'min_fraction' in kwargs
        assert 'max_fraction' in kwargs
        func = lambda: ic(g, **kwargs)
    else:
        raise ValueError('model {} unsupported'.format(cascade_model))

    while True:
        _, infection_times, _ = func()
        inf_nodes = set(infected_nodes(infection_times))
        if obs.issubset(inf_nodes):
            return inf_nodes
            break
        else:
            pass


def sample_by_simulation(
        g, obs,
        cascade_model,
        n_samples,
        debug=True,
        parallel=False,
        n_jobs=8,
        **kwargs
):
    samples = []
    obs = set(obs)

    if debug:
        iters = tqdm(range(n_samples), total=n_samples)
    else:
        iters = range(n_samples)

    if parallel:
        if debug:
            print('running in parallel[{}]'.format(n_jobs))
        tasks = (
            delayed(sample_one_by_simulation)(
                g, obs, cascade_model, **kwargs
            )
            for i in iters
        )
        samples = Parallel(n_jobs=n_jobs)(tasks)
    else:
        for i in iters:
            samples.append(
                sample_one_by_simulation(g, obs, cascade_model, **kwargs)
            )
    return samples


def sample_one_by_hybrid_simulation(
        g, obs, cascade_model,
        basis_generator,
        basis_kwargs,
        cascade_kwargs,
        max_tries=100
):
    """
    sample one cascade using the following steps

    1. first generate a basis subgraph g' that contains the `obs` nodes
    2. continue the simulation from g' using `cascade_model`

    Note: in case the basis_generator outputs too large inputs,
    the process will repeat until a small enough one is produced

    Exmaple of using random steiner tree to generate the basis:

    >> g, gi, obs, r, p, max_fraction = ...  # input
    >> sample_one_by_hybrid_simulation(
        g,
        obs,
        cascade_model='si',
        basis_generator=random_steiner_tree
        basis_kwargs=dict(gi=gi, X=obs, root=r, method='lerw'),
        cascade_kwargs=dict(p=0.5, source=r, max_fraction=0.1)
    )
    """
    for i in range(max_tries):
        try:
            infected = basis_generator(**basis_kwargs)
            cascade_kwargs['infected'] = infected
            return sample_one_by_simulation(g, obs, cascade_model, **cascade_kwargs)
        except TooManyInfections:
            continue
    raise TooManyInfections('after trying {} times'.format(max_tries))


def sample_by_hybrid_simulation(
        g, obs,
        cascade_model,
        n_samples,
        cascade_kwargs,
        basis_generator,
        basis_kwargs,
        debug=True,
        parallel=False,
        n_jobs=8
):
    """
    generate cascade via hybrid simulation. It's basically:

    1. form a basis subgraph that contains the observed nodes
    2. continue the simulation from the subgraph
    """
    samples = []
    obs = set(obs)

    if debug:
        iters = tqdm(range(n_samples), total=n_samples)
    else:
        iters = range(n_samples)

    args = (g, obs, cascade_model)
    kwargs = dict(
        basis_generator=basis_generator,
        basis_kwargs=basis_kwargs,
        cascade_kwargs=cascade_kwargs
    )

    if parallel:
        if debug:
            print('running in parallel[{}]'.format(n_jobs))
        tasks = (
            delayed(sample_one_by_hybrid_simulation)(
                *args, **kwargs
            )
            for i in iters
        )
        samples = Parallel(n_jobs=n_jobs)(tasks)
    else:
        for i in iters:
            samples.append(
                sample_one_by_hybrid_simulation(
                    *args, **kwargs
                )
            )
    return samples


def sample_by_mst_plus_simulation(
        g, obs,
        cascade_model,
        n_samples,
        cascade_kwargs,
        **kwargs
):
    """
    sample generation using minimum steiner tree (mst) + simulation
    """
    basis_generator = min_steiner_tree
    basis_kwargs = dict(
        g=g,
        obs_nodes=obs,
        return_type='nodes',
        debug=kwargs.get('debug', False),
        verbose=kwargs.get('verbose', False)
    )

    return sample_by_hybrid_simulation(
        g, obs,
        cascade_model, n_samples,
        cascade_kwargs=cascade_kwargs,
        basis_generator=basis_generator,
        basis_kwargs=basis_kwargs,
        **kwargs
    )


def sample_by_rst_plus_simulation(
        g, obs,
        cascade_model,
        n_samples,
        cascade_kwargs,
        **kwargs
):
    """
    sample generation using random steiner tree (rst) + simulation
    """
    def basis_generator(*args, **kwargs):
        edges = random_steiner_tree(*args, **kwargs)
        return [u for e in edges for u in e]

    basis_kwargs = dict(
        gi=from_gt(g),
        method='loop_erased',
        X=obs,
        root=cascade_kwargs['source']
    )
    
    return sample_by_hybrid_simulation(
        g, obs,
        cascade_model, n_samples,
        cascade_kwargs=cascade_kwargs,
        basis_generator=basis_generator,
        basis_kwargs=basis_kwargs,
        **kwargs
    )


def sample_by_reverse_reachable_set(
        g, obs,
        cascade_model,
        n_samples,
        cascade_kwargs,
        **kwargs
):
    """
    sample generation using Reverse Reachable Set
    
    https://www.slideshare.net/cigdemaslay/wsdm-2018-tutorial-on-influence-maximization-in-social-networks

    starting from page 72
    """
    # the basis generator simply returns the terminals X
    # it relies on the simulator to simulate infections from X
    def dummy_basis_generator():
        return set(list(obs))

    assert cascade_model.lower() == 'ic', 'only works for IC models for now'
    
    return sample_by_hybrid_simulation(
        g, obs,
        cascade_model,
        n_samples,
        cascade_kwargs=cascade_kwargs,
        basis_generator=dummy_basis_generator,
        basis_kwargs=dict(),
        **kwargs
    )
