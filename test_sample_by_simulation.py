import pytest
import numpy as np
from cascade_generator import (si, ic)
from fixture import g
from core import sample_by_simulation
from helpers import infected_nodes


@pytest.mark.parametrize(
    "cascade_model", ['ic', 'si']
)
def test_sample_by_simulation(g, cascade_model):
    n_obs = 5
    p = 0.5
    max_fraction = 0.5
    min_cascade_size = 10
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
                min_fraction=(min_cascade_size / g.num_vertices())
            )
            kwargs = dict(
                max_fraction=max_fraction
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
        
