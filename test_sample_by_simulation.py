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
    stop_fraction = 0.5
    min_cascade_size = 10
    n_samples = 5
    for i in range(3):
        if cascade_model == 'si':
            source, times, _ = si(
                g, p=p, source=None,
                stop_fraction=stop_fraction
            )
            kwargs = dict(
                stop_fraction=stop_fraction
            )
        elif cascade_model == 'ic':
            while True:
                source, times, _ = ic(
                    g, p=p, source=None,
                    min_size=min_cascade_size
                )
                if len(infected_nodes(times)) >= min_cascade_size:
                    break

            kwargs = dict(
                min_size=min_cascade_size
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
        
