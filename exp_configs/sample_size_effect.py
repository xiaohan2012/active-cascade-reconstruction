"""
compare different query strategies on different graphs and cascades
"""
from .base import ConfigBase
from itertools import product


class Config(ConfigBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.root_sampler = 'true_root'

        self.query_method = 'random'  # does not matter which
        self.query_n_samples = 0
        self.query_sampling_method = 'naive'
        self.pruning_proba = 0

        self.infer_every = -1  # just infer at the begining
        # self.n_rounds = 2
        # self.arg_suffix = '--verbose'

        self.n_queries = 0  # no query, just infer base on intial observation

        self.hours_per_job = 10
        self.minutes_per_job = 0

        self.metric_name='ap'

config_dimensions = [
    # datasets
    [
        # dict(
        #     graph='infectious',
        #     cascade_fraction=0.1,
        #     obs_fraction=0.1
        # ),
        dict(
            graph='email-univ',
            cascade_fraction=0.025,
            obs_fraction=0.1
        ),
        dict(
            graph='student',
            cascade_fraction=0.025,
            obs_fraction=0.1
        ),
        # dict(
        #     graph='lattice-100',
        #     cascade_fraction=0.25,
        #     obs_fraction=0.25,
        # )
    ],
    # cascade model
    [
        # dict(cascade_model="si"),
        dict(cascade_model="ic"),
    ],
    # infer sampling algorithm
    [
        # dict(infer_sampling_method='simulation'),
        # dict(infer_sampling_method='loop_erased'),
        # dict(infer_sampling_method='mst'),
        dict(infer_sampling_method='rst')
    ],
    [
        dict(infer_n_samples=10),
        dict(infer_n_samples=20),
        dict(infer_n_samples=40),
        dict(infer_n_samples=80),
        dict(infer_n_samples=160),
        dict(infer_n_samples=320),
        dict(infer_n_samples=640),
        dict(infer_n_samples=1280),
        dict(infer_n_samples=2560)
    ]
]

def iter_configs():
    for dict_list in product(*config_dimensions):
        params = {}
        for d in dict_list:
            params.update(d)
    
        yield Config(**params)
