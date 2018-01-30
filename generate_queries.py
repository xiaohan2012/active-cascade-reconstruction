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

# following applies to sampler approach
parser.add_argument('-n', '--n_queries', default=10, type=int,
                    help='number of queries')
parser.add_argument('-m', '--sampling_method', default='loop_erased', type=str,
                    choices={'loop_erased', 'cut', 'cut_naive'},
                    help='the steiner tree sampling method')
parser.add_argument('-r', '--root_sampler', default='earliest_nbrs', type=str,
                    choices={'earliest_obs', 'earliest_nbrs', 'pagerank', None},
                    help='the steiner tree sampling method')
parser.add_argument('-s', '--n_samples', default=100, type=int,
                    help='number of samples')

# specific to prediction error-based sampler
parser.add_argument('-p', '--min_proba', default=0.0, type=float,
                    help='(minimum) threshold used for pruning candidate nodes')
parser.add_argument('-e', '--num_estimation_nodes', default=None, type=int,
                    help='number of nodes used for error estimation')

parser.add_argument('-d', '--output_dir', default='outputs/queries', help='output directory')
parser.add_argument('-b', '--debug', action='store_true', help='if debug, use non-parallel')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='if verbose, verbose information is printed')

args = parser.parse_args()

graph_name = args.graph
n_queries = args.n_queries
n_samples = args.n_samples
root_sampler = args.root_sampler

# output_dir = '{}/{}'.format(args.output_dir, graph_name)
output_dir = args.output_dir
sampling_method = args.sampling_method
query_strategy = args.query_strategy

# for prediction error-based query selector
min_proba = args.min_proba
num_estimation_nodes = args.num_estimation_nodes

g = load_graph_by_name(graph_name)

if query_strategy == 'random':
    strategy = (RandomQueryGenerator, {})
elif query_strategy == 'pagerank':
    strategy = (PRQueryGenerator, {})
elif query_strategy == 'entropy':
    strategy = (EntropyQueryGenerator, {'method': 'entropy', 'root_sampler': root_sampler})
elif query_strategy == 'prediction_error':
    print("min_proba={}".format(min_proba))
    print("num_estimation_nodes={}".format(num_estimation_nodes))
    strategy = (PredictionErrorQueryGenerator, {'n_node_samples': None,
                                                'prune_nodes': True,
                                                'root_sampler': root_sampler,
                                                'min_proba': min_proba,
                                                'n_node_samples': num_estimation_nodes})
else:
    raise ValueError('invalid strategy name')


def one_round(g, obs, c, c_path, q_gen_cls, param, q_gen_name, output_dir, sampling_method, n_samples,
              verbose):
    stime = time.time()
    c_id = os.path.basename(c_path).split('.')[0]
    d = output_dir
    outpath = os.path.join(d, c_id + '.pkl')

    # meta data such as running time, etc
    meta_outpath = os.path.join(d, c_id + '.meta.pkl')

    if os.path.exists(outpath):
        print("{} processed already, skip".format(c_path))
        return

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

    q_gen = q_gen_cls(gv, *args, verbose=verbose, **param)
    sim = Simulator(gv, q_gen, gi=gi, print_log=verbose)

    qs = sim.run(n_queries, obs, c)

    time_cost = time.time() - stime

    if not os.path.exists(d):
        os.makedirs(d)
    print('\nprocessing {} done: taking {:.4f} secs\n'.format(c_path, time_cost))
    pkl.dump(qs, open(outpath, 'wb'))

    meta_data = {'time_elapsed': time_cost}
    pkl.dump(meta_data, open(meta_outpath, 'wb'))

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
