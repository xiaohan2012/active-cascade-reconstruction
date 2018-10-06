# coding: utf-8

import time
import pickle as pkl
import os
import argparse


from query_selection import (RandomQueryGenerator, EntropyQueryGenerator,
                             PRQueryGenerator, CondEntropyQueryGenerator,
                             SamplingBasedGenerator,
                             MutualInformationQueryGenerator,
                             EarliestFirstOracle, LatestFirstOracle)
from simulator import Simulator
from graph_helpers import remove_filters, load_graph_by_name, get_edge_weights
from helpers import cascade_source, timeout
from sample_pool import TreeSamplePool, SimulatedCascadePool
from random_steiner_tree.util import from_gt
from tree_stat import TreeBasedStatistics
from arg_helpers import (
    add_cascade_parameter_args
)
from config import QUERY_TIMEOUT


@timeout(seconds=QUERY_TIMEOUT)
def one_round(
        g,
        obs,
        c,
        c_path,
        query_strategy_cls,
        query_strategy_param,
        query_method_name,
        output_dir,
        sampling_method,
        n_samples,
        verbose,
        cmd_args
):
    """
    Generate queries for a single cascade and observation

    Params:
    ------------

    g: graph
    obs: list of observed infection
    c: cascade (list of infection time)
    c_path: cascade path
    query_strategy_cls: class of query strategy
    query_strategy_param: param to be passed when init the query strategy class

    """
    stime = time.time()
    c_id = os.path.basename(c_path).split('.')[0]
    d = output_dir
    outpath = os.path.join(d, c_id + '.pkl')

    # meta data such as running time, etc
    meta_outpath = os.path.join(d, c_id + '.meta.pkl')

    if os.path.exists(outpath):
        print("{} processed already, skip".format(c_path))
        return

    print('\nquerying {} started, using {}\n'.format(
        c_path, query_method_name
    ))

    gv = remove_filters(g)
    args = []  # sampling based method need a sampler to initialize

    weights = get_edge_weights(gv)
    gi = from_gt(gv, weights=weights)

    if issubclass(query_strategy_cls, SamplingBasedGenerator):
        if sampling_method == 'simulation':
            if verbose:
                print("loading simulation-based sampler")
                print("p={}".format(cmd_args.infection_proba))
                print("stop_fraction={}".format(cmd_args.cascade_size))

            cascade_params = dict(
                p=cmd_args.infection_proba,
                stop_fraction=cmd_args.cascade_size,
                cascade_model=cmd_args.cascade_model,
                source=cascade_source(c),
                debug=False  # turn it to True if you want to see more details
            )
            sampler = SimulatedCascadePool(
                gv, n_samples, cascade_params
            )
        else:
            sampler = TreeSamplePool(
                gv,
                n_samples=n_samples,
                method=sampling_method,
                gi=gi,
                return_type='nodes',
                with_resampling=False
            )
        args.append(sampler)
        query_strategy_param['error_estimator'] = TreeBasedStatistics(gv)
        
    q_gen = query_strategy_cls(gv, *args, verbose=verbose, **query_strategy_param)
    sim = Simulator(gv, q_gen, gi=gi, print_log=verbose)

    qs = sim.run(n_queries, obs, c)

    time_cost = time.time() - stime

    if not os.path.exists(d):
        os.makedirs(d)

    print("""
    query done:

    - cascade_path: {cascade_path}
    - query_method_name: {query_method_name}
    - sampling_method: {sampling_method}
    - time cost: {time_cost} s
    - output path {output_dir}

    """.format(
        cascade_path=c_path,
        query_method_name=query_method_name,
        sampling_method=sampling_method,
        time_cost=time_cost,
        output_dir=outpath
    ))
        
    pkl.dump(qs, open(outpath, 'wb'))

    meta_data = {'time_elapsed': time_cost}
    pkl.dump(meta_data, open(meta_outpath, 'wb'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-g', '--graph',
                        required=True,
                        help='graph name')
    parser.add_argument('-f', '--graph_suffix',
                        required=True,
                        help='suffix of graph name')

    parser.add_argument('-q', '--query_strategy',
                        required=True,
                        choices={'random',
                                 'pagerank',
                                 'entropy',
                                 'cond-entropy',
                                 'mutual-info',
                                 'oracle-e',
                                 'oracle-l'},
                        help='query strategy')
    parser.add_argument('-c', '--cascade_path',
                        help='path of generated cascade')

    # following applies to sampler approach
    parser.add_argument('-n', '--n_queries', default=10, type=int,
                        help='number of queries')
    parser.add_argument('-m', '--sampling_method', default='loop_erased', type=str,
                        choices={'loop_erased', 'cut', 'cut_naive', 'simulation'},
                        help='the steiner tree sampling method')
    parser.add_argument('-r', '--root_sampler', type=str,
                        default='pagerank',
                        choices={'pagerank', 'random', 'true_root'},
                        help='the steiner tree sampling method')
    parser.add_argument('-s', '--n_samples', default=100, type=int,
                        help='number of samples')

    # specific to prediction error-based sampler
    parser.add_argument('-p', '--min_proba', default=0.0, type=float,
                        help='(minimum) threshold used for pruning candidate nodes')
    parser.add_argument('-e', '--num_estimation_nodes', default=None, type=int,
                        help='number of nodes used for error estimation')

    parser.add_argument('-d', '--output_dir', required=True, help='output path')
    parser.add_argument('-b', '--debug', action='store_true', help='if debug, use non-parallel')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='if verbose, verbose information is printed')

    # specific to pagerank root sampler
    parser.add_argument('--root_pagerank_noise', default=0.0, type=float,
                        help='the epsilon value for pagerank root sampling, the higher the more noisy')

    add_cascade_parameter_args(parser)

    args = parser.parse_args()

    print("Args:")
    print('-' * 10)
    for k, v in args._get_kwargs():
        print("{}={}".format(k, v))
            
    graph_name = args.graph
    graph_suffix = args.graph_suffix

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

    g = load_graph_by_name(graph_name, weighted=False,
                           suffix=graph_suffix)

    if query_strategy == 'random':
        strategy = (RandomQueryGenerator, {})
    elif query_strategy == 'oracle-e':
        strategy = (EarliestFirstOracle, {})
    elif query_strategy == 'oracle-l':
        strategy = (LatestFirstOracle, {})
    elif query_strategy == 'pagerank':
        strategy = (PRQueryGenerator, {})
    elif query_strategy == 'entropy':
        strategy = (EntropyQueryGenerator, {'method': 'entropy', 'root_sampler': root_sampler,
                                            'root_sampler_eps': args.root_pagerank_noise})
    elif query_strategy == 'cond-entropy':
        print("min_proba={}".format(min_proba))
        print("num_estimation_nodes={}".format(num_estimation_nodes))
        strategy = (CondEntropyQueryGenerator, {'n_node_samples': None,
                                                'prune_nodes': True,
                                                'root_sampler': root_sampler,
                                                'root_sampler_eps': args.root_pagerank_noise,
                                                'min_proba': min_proba,
                                                'n_node_samples': num_estimation_nodes})

    elif query_strategy == 'mutual-info':
        strategy = (MutualInformationQueryGenerator,
                    {'n_node_samples': None,
                     'prune_nodes': True,
                     'root_sampler': root_sampler,
                     'root_sampler_eps': args.root_pagerank_noise,
                     'min_proba': min_proba,
                     'n_node_samples': num_estimation_nodes})
    else:
        raise ValueError('invalid strategy name')

    obs, c = pkl.load(open(args.cascade_path, 'rb'))
    strategy_cls, strategy_param = strategy
    one_round(
        g,
        obs,
        c,
        args.cascade_path,
        strategy_cls,
        strategy_param,
        query_strategy,
        output_dir,
        sampling_method,
        n_samples,
        args.verbose,
        args
    )
