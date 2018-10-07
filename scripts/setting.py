CASCADE_ROOT_DIR = '/experiment/cascades'
OUTPUT_ROOT_DIR = '/experiment/outputs'


GRAPHS = ("student", )
QUERY_METHODS = ('cond-entropy', 'entropy', 'pagerank', 'random')

# this is VERY important for simulated-based sampler
# if it's too big (e.g, > casade size), it's extremely hard to accept the samples
# I would suggest making N_QUERIES  smaller than num. hidden infections
# for example, for infectious (|V|=410)+ cascade_size = 0.1 and OBS_FRACTION = 0.1
# #hidden nodes = 36.9
# I would set N_QUERIES=15
N_QUERIES = 30

N_ROUNDS = 96
ARG_SUFFIX = '--verbose --debug'


INFECTION_PROBA = 0.5
GRAPH_SUFFIX = "_{}".format(INFECTION_PROBA)

CASCADE_MODEL = "si"
CASCADE_FRACTION = 0.025
OBS_FRACTION = 0.1
OBS_METHOD = "uniform"

N_SAMPLES = 100  # 2500
SAMPLING_METHOD = "simulation"

ROOT_SAMPLER = 'true_root'
    

PRUNING_PROBA = 0.05

EVAL_EVERY = 3

def get_dataset_id(graph):
    return "{graph}-m{cascade_model}-s{cascade_fraction}-o{obs_fraction}-omuniform".format(
        graph=graph,
        cascade_model=CASCADE_MODEL,
        cascade_fraction=CASCADE_FRACTION,
        obs_fraction=OBS_FRACTION
    )

def get_cascade_dir(dataset_id):
    return "{cascade_root_dir}/{dataset_id}".format(
        cascade_root_dir=CASCADE_ROOT_DIR,
        dataset_id=dataset_id
    )

def get_query_dir(dataset_id, query_method):
    return '{output_root_dir}/queries/{dataset_id}/{sample_method}/{query_method}'.format(
        output_root_dir=OUTPUT_ROOT_DIR,
        dataset_id=dataset_id,
        sample_method=SAMPLING_METHOD,
        query_method=query_method
    )

def get_inference_dir(dataset_id, query_method):
    return '{output_root_dir}/inference/{dataset_id}/{sample_method}/{query_method}'.format(
        output_root_dir=OUTPUT_ROOT_DIR,
        dataset_id=dataset_id,
        sample_method=SAMPLING_METHOD,
        query_method=query_method
    )
