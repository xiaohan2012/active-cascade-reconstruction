# coding: utf-8

import time
import pickle as pkl
import os
import argparse

from tqdm import tqdm

from query_selection import (RandomQueryGenerator, EntropyQueryGenerator,
                             PRQueryGenerator, PredictionErrorQueryGenerator,
                             SamplingBasedGenerator)
from simulator import Simulator
from joblib import Parallel, delayed
from graph_helpers import remove_filters, load_graph_by_name
from helpers import load_cascades
from sample_pool import TreeSamplePool
from random_steiner_tree.util import from_gt
from tree_stat import TreeBasedStatistics

parser = argparse.ArgumentParser(description='')
parser.add_argument('-g', '--graph', help='graph name')
parser.add_argument('-q', '--query_strategy',
                    choices={'random', 'pagerank', 'entropy', 'prediction_error'},
                    help='query strategy')
parser.add_argument('-c', '--cascade_dir',
                    help='directory of generated cascades')
parser.add_argument('-n', '--n_queries', default=10, type=int,
                    help='number of queries')
parser.add_argument('-m', '--sampling_method', default='loop_erased', type=str,
                    choices={'loop_erased', 'cut', 'cut_naive'},
                    help='the steiner tree sampling method')
parser.add_argument('-s', '--n_samples', default=100, type=int,
                    help='number of samples')

parser.add_argument('-d', '--output_dir', default='outputs/queries', help='output directory')
parser.add_argument('-b', '--debug', action='store_true', help='if debug, use non-parallel')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='if verbose, verbose information is printed')

args = parser.parse_args()

graph_name = args.graph
n_queries = args.n_queries
n_samples = args.n_samples
# output_dir = '{}/{}'.format(args.output_dir, graph_name)
output_dir = args.output_dir
sampling_method = args.sampling_method
query_strategy = args.query_strategy

g = load_graph_by_name(graph_name)

if query_strategy == 'random':
    strategy = (RandomQueryGenerator, {})
elif query_strategy == 'pagerank':
    strategy = (PRQueryGenerator, {})
elif query_strategy == 'entropy':
    strategy = (EntropyQueryGenerator, {'method': 'entropy', 'root_sampler': 'earliest_nbrs'})
elif query_strategy == 'prediction_error':
    strategy = (PredictionErrorQueryGenerator, {'n_node_samples': 500, 'prune_nodes': True,
                                                'root_sampler': 'earliest_nbrs'})
else:
    raise ValueError('invalid strategy name')


def one_round(g, obs, c, c_path, q_gen_cls, param, q_gen_name, output_dir, sampling_method, n_samples,
              verbose):
    stime = time.time()
    print('\nprocessing {} started\n'.format(c_path))
    gv = remove_filters(g)
    args = []
    # sampling based method need a sampler to initialize
    gi = from_gt(g)
    if issubclass(q_gen_cls, SamplingBasedGenerator):
        sampler = TreeSamplePool(
            gv,
            n_samples=n_samples,
            method=sampling_method,
            gi=gi,
            return_tree_nodes=True)
        args.append(sampler)

    if issubclass(q_gen_cls, PredictionErrorQueryGenerator):
        param['error_estimator'] = TreeBasedStatistics(gv)

    q_gen = q_gen_cls(gv, *args, **param)
    sim = Simulator(gv, q_gen, gi=gi, print_log=verbose)

    qs = sim.run(n_queries, obs, c)

    d = output_dir
    if not os.path.exists(d):
        os.makedirs(d)
    c_id = os.path.basename(c_path).split('.')[0]
    outpath = os.path.join(d, c_id + '.pkl')
    pkl.dump(qs, open(outpath, 'wb'))
    print('\nprocessing {} done: taking {:.4f} secs\n'.format(c_path, time.time() - stime))

cascade_generator = load_cascades(args.cascade_dir)


# run!
if args.debug:
    print('====================')
    print('DEBUG MODE')
    print('====================')
    cls, param = strategy
    for path, (obs, c) in tqdm(cascade_generator):
        one_round(g, obs, c, path, cls, param, query_strategy, output_dir, sampling_method, n_samples,
                  args.verbose)
else:
    Parallel(n_jobs=-1)(delayed(one_round)(g, obs, c, path, strategy[0], strategy[1],
                                           query_strategy, output_dir, sampling_method, n_samples,
                                           args.verbose)
                        for path, (obs, c) in tqdm(cascade_generator))
