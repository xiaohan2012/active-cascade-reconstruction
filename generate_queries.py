# coding: utf-8

import pickle as pkl
import os
import argparse

from tqdm import tqdm

from query_selection import (RandomQueryGenerator, EntropyQueryGenerator,
                             PRQueryGenerator, PredictionErrorQueryGenerator)
from simulator import Simulator
from joblib import Parallel, delayed
from graph_helpers import remove_filters, load_graph_by_name
from helpers import load_cascades

parser = argparse.ArgumentParser(description='')
parser.add_argument('-g', '--graph', help='graph name')

parser.add_argument('-c', '--cascade_dir',
                    help='directory of generated cascades')
parser.add_argument('-n', '--n_queries', default=10, type=int,
                    help='number of queries')
parser.add_argument('-s', '--n_samples', default=100, type=int,
                    help='number of samples')

parser.add_argument('-d', '--output_dir', default='outputs/queries', help='output directory')
parser.add_argument('-b', '--debug', action='store_true', help='if debug, use non-parallel')

args = parser.parse_args()

graph_name = args.graph
n_queries = args.n_queries
n_samples = args.n_samples
# output_dir = '{}/{}'.format(args.output_dir, graph_name)
output_dir = args.output_dir


g = load_graph_by_name(graph_name)


strategies = [
    # (RandomQueryGenerator, {}, 'random'),
    # (PRQueryGenerator, {}, 'pagerank'),
    # (EntropyQueryGenerator, {'num_stt': n_samples, 'method': 'entropy', 'use_resample': False}, 'entropy'),
    (PredictionErrorQueryGenerator, {'num_stt': n_samples}, 'prediction_error'),
]


def one_round(g, obs, c, c_path, q_gen_cls, param, q_gen_name, output_dir):

    gv = remove_filters(g)
    q_gen = q_gen_cls(gv, **param)
    sim = Simulator(gv, q_gen)

    qs = sim.run(n_queries, obs, c)
    
    d = os.path.join(output_dir, q_gen_name)
    if not os.path.exists(d):
        os.makedirs(d)
    c_id = os.path.basename(c_path).split('.')[0]
    outpath = os.path.join(d, c_id + '.pkl')
    pkl.dump(qs, open(outpath, 'wb'))
    
cascade_generator = load_cascades(args.cascade_dir)


# run!
if args.debug:
    print('====================')
    print('DEBUG MODE')
    print('====================')
    for path, (obs, c) in tqdm(cascade_generator):
        for cls, param, name in strategies:
            one_round(g, obs, c, path, cls, param, name, output_dir)
else:
    Parallel(n_jobs=-1)(delayed(one_round)(g, obs, c, path, cls, param, name, output_dir)
                        for path, (obs, c) in tqdm(cascade_generator)
                        for cls, param, name in strategies)
        

