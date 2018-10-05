import os
from itertools import product


CASCADE_ROOT_DIR = '/experiment/cascades'
OUTPUT_ROOT_DIR = '/experiment/outputs'

GRAPHS = ("infectious", "student", "email-univ")
QUERY_METHODS = ('cond-entropy', 'entropy', 'pagerank', 'random')


N_ROUNDS = 96
ARG_SUFFIX = '--verbose --debug'


INFECTION_PROBA = 0.5
GRAPH_SUFFIX = "_{}".format(INFECTION_PROBA)

CASCADE_MODEL = "si"
CASCADE_FRACTION = 0.1
OBS_FRACTION = 0.1
OBS_METHOD = "uniform"


N_SAMPLES = 100  # 2500
SAMPLING_METHOD = "simulation"

ROOT_SAMPLER = 'true_root'


# this is VERY important for simulated-based sampler
# if it's too big (e.g, > casade size), it's extremely hard to accept the samples
# I would suggest making N_QUERIES slightly  smaller than #hidden infections
# for example, for infectious (|V|=410)+ cascade_size = 0.1 and OBS_FRACTION = 0.1
# #hidden nodes = 36.9
# I would set N_QUERIES=15
N_QUERIES = 15

PRUNING_PROBA = 0.05

for graph, query_method in product(GRAPHS, QUERY_METHODS):
    dataset_id = "{graph}-m{cascade_model}-s{cascade_fraction}-o{obs_fraction}-omuniform".format(
        graph=graph,
        cascade_model=CASCADE_MODEL,
        cascade_fraction=CASCADE_FRACTION,
        obs_fraction=OBS_FRACTION
    )
    cascade_dir = "{cascade_root_dir}/{dataset_id}".format(
        cascade_root_dir=CASCADE_ROOT_DIR,
        dataset_id=dataset_id
    )
    for i in range(N_ROUNDS):
        cascade_path = os.path.join(cascade_dir, '{}.pkl'.format(i))
        output_dir = '{output_root_dir}/{dataset_id}/{sample_method}/{query_method}'.format(
            output_root_dir=OUTPUT_ROOT_DIR,
            dataset_id=dataset_id,
            sample_method=SAMPLING_METHOD,
            query_method=query_method
        )
        arguments = [
            ('-g', graph),
            ('-f', GRAPH_SUFFIX),
            ('-q', query_method),
            ('-n', N_QUERIES),
            ('-s', N_SAMPLES),
            ('-p', PRUNING_PROBA),
            ('-m', SAMPLING_METHOD),
            ('-r', ROOT_SAMPLER),
            ('-c', cascade_path),
            ('-d', output_dir),
            ('--infection_proba', INFECTION_PROBA),
            ('--cascade_size', CASCADE_FRACTION),
            ('--cascade_model', CASCADE_MODEL)
        ]

        str_list = []
        for name, value in arguments:
            str_list.append('{} {}'.format(name, value))

        arg_str = ' '.join(str_list)
        arg_str += (" " + ARG_SUFFIX)
        print(arg_str)

