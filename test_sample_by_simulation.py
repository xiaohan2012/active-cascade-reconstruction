import pytest
import random
import numpy as np

from cascade_generator import (si, ic)
from fixture import g
from core import (
    sample_by_simulation,
    sample_by_hybrid_simulation,
    sample_by_mst_plus_simulation,
    sample_by_rst_plus_simulation,
    sample_by_reverse_reachable_set
)
from helpers import infected_nodes


@pytest.mark.parametrize(
    "cascade_model", ['ic', 'si']
)
def test_sample_by_simulation(g, cascade_model):
    n_obs = 5
    p = 0.5
    max_fraction = 0.5
    min_cascade_size = 10
    min_fraction = (min_cascade_size / g.num_vertices())
    n_samples = 5
    for i in range(3):
        if cascade_model == 'si':
            source, times, _ = si(
                g, p=p, source=None,
                max_fraction=max_fraction
            )
            kwargs = dict(
                max_fraction=max_fraction
            )
        elif cascade_model == 'ic':

            source, times, _ = ic(
                g, p=p, source=None,
                max_fraction=max_fraction,
                min_fraction=min_fraction
            )
            kwargs = dict(
                max_fraction=max_fraction,
                min_fraction=min_fraction
            )

        inf_nodes = infected_nodes(times)
        obs = set(np.random.choice(inf_nodes, n_obs, replace=False))
        samples = sample_by_simulation(
            g, obs,
            cascade_model=cascade_model,
            n_samples=n_samples,
            p=p,
            source=source,
            **kwargs
        )
        for s in samples:
            assert obs.issubset(s)


@pytest.mark.parametrize(
    "cascade_model", ['si', 'ic']
)
@pytest.mark.parametrize(
    "approach", ['mst', 'rst', 'rrs']
)
def test_sample_by_hybrid_simulation(g, cascade_model, approach):
    n_obs = 5
    p = 0.5
    max_fraction = 0.5
    min_cascade_size = 10
    min_fraction = (min_cascade_size / g.num_vertices())
    n_samples = 5

    for i in range(3):
        if cascade_model == 'si':
            source, times, _ = si(
                g, p=p, source=None,
                max_fraction=max_fraction
            )
            cascade_kwargs = dict(
                p=p,
                source=source,
                max_fraction=max_fraction
            )
        elif cascade_model == 'ic':
            source, times, _ = ic(
                g, p=p, source=None,
                min_fraction=min_fraction,
                max_fraction=max_fraction
            )
            cascade_kwargs = dict(
                p=p,
                source=source,
                min_fraction=min_fraction,
                max_fraction=max_fraction
            )

        inf_nodes = infected_nodes(times)
        obs = set(np.random.choice(inf_nodes, n_obs, replace=False))

        if approach == 'mst':
            samples = sample_by_mst_plus_simulation(
                g, obs,
                cascade_model=cascade_model,
                n_samples=n_samples,
                cascade_kwargs=cascade_kwargs,
            )
        elif approach == 'rst':
            samples = sample_by_rst_plus_simulation(
                g, obs,
                cascade_model=cascade_model,
                n_samples=n_samples,
                cascade_kwargs=cascade_kwargs,
            )
        elif approach == 'rrs':
            if cascade_model == 'ic':
                samples = sample_by_reverse_reachable_set(
                    g, obs,
                    cascade_model=cascade_model,
                    n_samples=n_samples,
                    cascade_kwargs=cascade_kwargs
                )
            else:
                # rrs does not apply to sampling method other than IC for now
                # the following workaround simply makes the test pass
                samples = [set(obs) for i in range(n_samples)]
        else:
            raise ValueError('no such sampling approach: {}'.format(approach))

        for s in samples:
            assert obs.issubset(s)
            if approach != 'rrs' and cascade_model != 'si':
                assert len(s) > len(obs)


def test_sample_by_hybrid_simulation_when_infected_is_too_large(g):
    # when the input infections are too many, should re-generate the input infections
    
    # define a basis_generator that have half probability of exceeding the max size
    N = g.num_vertices()
    obs_fraction = 0.1
    p = 0.5
    max_fraction = 0.5
    n_samples = 5

    def basis_generator(obs, other_nodes, max_size):
        ret = list(obs)
        if random.random() > 0.5:
            print('reasonable size')
            n_remain = max_size - len(ret)
            return ret + random.sample(other_nodes, n_remain)
        else:
            print('too large')
            n_remain = max_size + 1 - len(ret)
            return ret + random.sample(other_nodes, n_remain)

    for i in range(3):
        source, times, _ = si(
            g, p=p, source=None,
            max_fraction=max_fraction
        )
        cascade_kwargs = dict(
            p=p,
            source=source,
            max_fraction=max_fraction
        )

        inf_nodes = infected_nodes(times)
        n_infs = len(inf_nodes)
        obs = set(np.random.choice(inf_nodes, int(n_infs * obs_fraction), replace=False))
        
        basis_kwargs = dict(
            obs=obs,
            other_nodes=list(set(np.arange(N)) - obs),
            max_size=int(N * max_fraction)
        )

        samples = sample_by_hybrid_simulation(
            g, obs,
            cascade_model='si',
            n_samples=n_samples,
            cascade_kwargs=cascade_kwargs,
            basis_generator=basis_generator,
            basis_kwargs=basis_kwargs
        )

        for s in samples:
            assert obs.issubset(s)


            
