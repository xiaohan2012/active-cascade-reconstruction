import os
from itertools import product
from setting import *


for graph, query_method in product(GRAPHS, QUERY_METHODS):
    dataset_id = get_dataset_id(graph)
    cascade_dir = get_cascade_dir(dataset_id)
    for i in range(N_ROUNDS):
        cascade_path = os.path.join(cascade_dir, '{}.pkl'.format(i))
        output_dir = get_query_dir(dataset_id, query_method)
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

