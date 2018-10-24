"""
experiment configurations
"""
import sys
import os


class ConfigBase:
    """base class for the config on one set of experiments

    specifically for:
    - 1 graph
    - 1 query method
    - 1 sampling method
    """
    def __init__(
            self,
            # graph related
            graph=None,
            graph_suffix='_0.5',
            # query method related
            query_method=None,
            n_queries=None,
            query_sampling_method=None,
            query_n_samples=None,
            root_sampler=None,
            pruning_proba=None,
            n_rounds=96,
            # cascade model related
            cascade_model=None,
            cascade_fraction=None,
            obs_fraction=None,
            obs_method='uniform',
            cascade_root_dir='/experiment/cascades',
            infection_proba=0.5,
            # inference related
            infer_sampling_method='simulation',
            infer_n_samples=None,
            infer_every=None,
            # misc
            arg_suffix='',
            # runtime
            hours_per_job=1
    ):
        self.cascade_root_dir = cascade_root_dir

        self.graph = graph
        self.graph_suffix = graph_suffix
        self.query_method = query_method
        self.n_queries = n_queries

        self.n_rounds = n_rounds

        self.cascade_model = cascade_model
        self.cascade_fraction = cascade_fraction
        self.obs_fraction = obs_fraction
        self.obs_method = obs_method
        self.infection_proba = infection_proba

        self.query_sampling_method = query_sampling_method
        self.query_n_samples = query_n_samples
        self.root_sampler = root_sampler
        self.pruning_proba = pruning_proba

        self.infer_sampling_method = infer_sampling_method
        self.infer_n_samples = infer_n_samples        
        self.infer_every = infer_every

        self.arg_suffix = arg_suffix

        self.hours_per_job = hours_per_job
    
    def get_dataset_id(self):
        kwargs = dict(
            graph=self.graph,
            cascade_model=self.cascade_model,
            cascade_fraction=self.cascade_fraction,
            obs_fraction=self.obs_fraction
        )
        for k, v in kwargs.items():
            assert v is not None, k
        return "{graph}-m{cascade_model}-s{cascade_fraction}-o{obs_fraction}-omuniform".format(
            **kwargs
        )

    def get_cascade_dir(self, dataset_id):
        kwargs = dict(
            cascade_root_dir=self.cascade_root_dir,
            dataset_id=dataset_id
        )
        for k, v in kwargs.items():
            assert v is not None, k
        return "{cascade_root_dir}/{dataset_id}".format(
            **kwargs
        )

    def print_query_params(self, fileobj=sys.stdout):
        dataset_id = self.get_dataset_id()
        cascade_dir = self.get_cascade_dir(dataset_id)
        for i in range(self.n_rounds):
            cascade_path = os.path.join(cascade_dir, '{}.pkl'.format(i))
            arguments = [
                ('-g', self.graph),
                ('-f', self.graph_suffix),
                ('-q', self.query_method),
                ('-n', self.n_queries),
                ('-s', self.query_n_samples),
                ('-p', self.pruning_proba),
                ('-m', self.query_sampling_method),
                ('-r', self.root_sampler),
                ('--dataset', dataset_id),
                ('-c', cascade_path),
                ('--infection_proba', self.infection_proba),
                ('--cascade_size', self.cascade_fraction),
                ('--cascade_model', self.cascade_model)
            ]

            str_list = []
            for name, value in arguments:
                str_list.append('{} {}'.format(name, value))

            arg_str = ' '.join(str_list)
            arg_str += (" " + self.arg_suffix)
            fileobj.write(arg_str + '\n')


    def print_infer_params(self, fileobj=sys.stdout):
        dataset_id = self.get_dataset_id()
        cascade_dir = self.get_cascade_dir(dataset_id)
        for i in range(self.n_rounds):
            cascade_path = os.path.join(cascade_dir, '{}.pkl'.format(i))
            arguments = [
                ('-g', self.graph),
                ('-f', self.graph_suffix),
                ('--dataset', dataset_id),
                ('-c', cascade_path),
                ('--inference_n_samples', self.infer_n_samples),
	        ('--inference_sampling_method', self.infer_sampling_method),
	        ('--query_method', self.query_method),
	        ('--n_queries', self.n_queries),
	        ('--query_sampling_method', self.query_sampling_method),
	        ('--root_sampler', self.root_sampler),
	        ('--query_n_samples', self.query_n_samples),
	        ('--min_proba', self.pruning_proba),
	        ('--infection_proba', self.infection_proba),
	        ('--cascade_size', self.cascade_fraction),
                ('--cascade_model', self.cascade_model),                
                ('--infer_every', self.infer_every)
            ]

            str_list = []
            for name, value in arguments:
                str_list.append('{} {}'.format(name, value))

            arg_str = ' '.join(str_list)
            arg_str += (" " + self.arg_suffix)
            fileobj.write(arg_str + '\n')

    @property
    def n_jobs(self):
        return self.n_rounds
