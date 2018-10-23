import os
from itertools import product
from setting import *


for graph, query_method in product(GRAPHS, QUERY_METHODS):
    dataset_id = get_dataset_id(graph)
    cascade_dir = get_cascade_dir(dataset_id)
    for i in range(N_ROUNDS):
        cascade_path = os.path.join(cascade_dir, '{}.pkl'.format(i))
        query_dir = get_query_dir(dataset_id, query_method)
        output_dir = get_inference_dir(dataset_id, query_method)
        arguments = [
            ('-g', graph),
            ('-f', GRAPH_SUFFIX),
            ('--query_method', query_method),
            ('-s', N_SAMPLES),
            ('-p', PRUNING_PROBA),
            # note we use "simulation" here as sampling_method 
            # as it's set to "simulation" by default
            # we do not specify it here
            ('-c', cascade_path),
            ('-q', query_dir),
            ('-p', output_dir),
            ('--infection_proba', INFECTION_PROBA),
            ('--cascade_size', CASCADE_FRACTION),
            ('--cascade_model', CASCADE_MODEL),
            ('--eval_every', EVAL_EVERY)
        ]

        str_list = []
        for name, value in arguments:
            str_list.append('{} {}'.format(name, value))

        arg_str = ' '.join(str_list)
        arg_str += (" " + ARG_SUFFIX)
        print(arg_str)
