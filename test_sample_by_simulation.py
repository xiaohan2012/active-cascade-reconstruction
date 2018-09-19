import numpy as np
from cascade_generator import si
from fixture import g
from core import sample_by_simulation
from helpers import infected_nodes

def test_sample_by_simulation(g):
    n_obs = 5
    p = 0.5
    stop_fraction = 0.5
    n_samples = 5
    for i in range(3):
        source, times, _ = si(
            g, p=p, source=None,
            stop_fraction=stop_fraction
        )

        inf_nodes = infected_nodes(times)
        obs = set(np.random.choice(inf_nodes, n_obs, replace=False))
        samples = sample_by_simulation(
            g, obs,
            cascade_model='si',
            n_samples=n_samples,
            p=p,
            source=source,
            stop_fraction=stop_fraction
        )
        for s in samples:
            assert obs.issubset(s)
        
