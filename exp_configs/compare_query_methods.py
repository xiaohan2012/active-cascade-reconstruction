"""
compare different query strategies on different graphs and cascades
"""
from .base import ConfigBase
from itertools import product


class Config(ConfigBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.pruning_proba = 0.05
        self.root_sampler = 'true_root'
        self.query_n_samples = 100
        self.query_sampling_method = 'simulation'

        self.infer_n_samples = 100
        self.infer_every = 3
        # self.n_rounds = 2
        # self.arg_suffix = '--verbose --debug'

        self.hours_per_job = 3

config_dimensions = [
    # graph and cascade related
    [
        dict(
            graph='infectious',
            n_queries=30,
            cascade_fraction=0.1,
            obs_fraction=0.1
        ),
        dict(
            graph='email-univ',
            n_queries=30,
            cascade_fraction=0.025,
            obs_fraction=0.1
        ),
        dict(
            graph='student',
            n_queries=30,
            cascade_fraction=0.025,
            obs_fraction=0.1
        ),
        dict(
            graph='lattice-100',
            n_queries=30,
            cascade_fraction=0.25,
            obs_fraction=0.25,
        )
    ],
    # query related
    [
        dict(query_method='random'),
        dict(query_method='pagerank'),
        dict(query_method='entropy')
    ],
    # cascade model
    [
        dict(cascade_model='ic')
    ]    
]

def iter_configs():
    for dict_list in product(*config_dimensions):
        params = {}
        for d in dict_list:
            params.update(d)
    
        yield Config(**params)
