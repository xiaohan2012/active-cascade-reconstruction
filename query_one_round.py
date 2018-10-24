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
from graph_helpers import (
    remove_filters,
    load_graph_by_name,
    get_edge_weights
)
from helpers import (
    cascade_source,
    timeout,
    get_now,
    init_db,
    get_query_result
)
from sample_pool import TreeSamplePool, SimulatedCascadePool
from tree_stat import TreeBasedStatistics
from random_steiner_tree.util import from_gt
from arg_helpers import (
    add_input_args,
    add_query_method_args,
    add_cascade_parameter_args
)
from config import QUERY_TIMEOUT, DB_CONFIG


@timeout(seconds=QUERY_TIMEOUT)
def one_round(
        g,
        obs,
        c,
        c_path,
        query_strategy_cls,
        query_strategy_param,
        query_method_name,
        n_queries,
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

    print('\nquerying {} started, using {}\n'.format(
        c_path, query_method_name
    ))

    gv = remove_filters(g)
    args = []  # sampling based method need a sampler to initialize

    gi = None
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
            weights = get_edge_weights(gv)
            gi = from_gt(gv, weights=weights)
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

    print("""
    query done:

    - cascade_path: {cascade_path}
    - query_method: {query_method_name}
    - sampling_method: {sampling_method}
    - time cost: {time_cost} s

    """.format(
        cascade_path=c_path,
        query_method_name=query_method_name,
        sampling_method=sampling_method,
        time_cost=time_cost
    ))
    ans = dict(
        qs=qs,
        time_cost=time_cost
    )
    return ans

    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')

    add_input_args(parser)
    add_query_method_args(parser)
    add_cascade_parameter_args(parser)

    parser.add_argument('-b', '--debug', action='store_true', help='if debug, use non-parallel')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='if verbose, verbose information is printed')
    

    args = parser.parse_args()

    print("Args:")
    print('-' * 10)
    for k, v in args._get_kwargs():
        print("{}={}".format(k, v))
            
    graph_name = args.graph
    graph_suffix = args.graph_suffix

    n_queries = args.n_queries
    n_samples = args.query_n_samples
    root_sampler = args.root_sampler

    sampling_method = args.query_sampling_method
    query_method = args.query_method

    # for prediction error-based query selector
    min_proba = args.min_proba
    num_estimation_nodes = args.num_estimation_nodes

    g = load_graph_by_name(graph_name, weighted=False,
                           suffix=graph_suffix)

    if query_method == 'random':
        strategy = (RandomQueryGenerator, {})
    elif query_method == 'oracle-e':
        strategy = (EarliestFirstOracle, {})
    elif query_method == 'oracle-l':
        strategy = (LatestFirstOracle, {})
    elif query_method == 'pagerank':
        strategy = (PRQueryGenerator, {})
    elif query_method == 'entropy':
        strategy = (EntropyQueryGenerator, {'method': 'entropy', 'root_sampler': root_sampler,
                                            'root_sampler_eps': args.root_pagerank_noise})
    elif query_method == 'cond-entropy':
        print("min_proba={}".format(min_proba))
        print("num_estimation_nodes={}".format(num_estimation_nodes))
        strategy = (
            CondEntropyQueryGenerator,
            {
                'prune_nodes': True,
                'root_sampler': root_sampler,
                'root_sampler_eps': args.root_pagerank_noise,
                'min_proba': min_proba,
                'n_node_samples': num_estimation_nodes
            }
        )

    elif query_method == 'mutual-info':
        strategy = (
            MutualInformationQueryGenerator,
            {
                'prune_nodes': True,
                'root_sampler': root_sampler,
                'root_sampler_eps': args.root_pagerank_noise,
                'min_proba': min_proba,
                'n_node_samples': num_estimation_nodes
            }
        )
    else:
        raise ValueError('invalid strategy name')

    obs, c = pkl.load(open(args.cascade_path, 'rb'))

    # database init
    conn, cursor = init_db(args.debug)

    stime = time.time()
    c_id = int(os.path.basename(args.cascade_path).split('.')[0])

    row = get_query_result(
        cursor,
        args.dataset,
        c_id,
        query_method,
        sampling_method,
        n_samples,
        args.n_queries,
        args.root_sampler,
        args.min_proba
    )
    if row is not None:
        print("processed already, skip")
        conn.close()
    else:    
        strategy_cls, strategy_param = strategy
        output = one_round(
            g,
            obs,
            c,
            args.cascade_path,
            strategy_cls,
            strategy_param,
            query_method,
            n_queries,
            sampling_method,
            n_samples,
            args.verbose,
            args
        )

        qs, time_cost = output['qs'], output['time_cost']

        data_to_insert = dict(
            dataset=args.dataset,
            cascade_id=c_id,
            query_method=query_method,
            sampling_method=sampling_method,
            n_samples=n_samples,
            n_queries=args.n_queries,
            root_sampler=args.root_sampler,
            pruning_proba=args.min_proba,
            queries=pkl.dumps(qs),
            time_elapsed=time_cost,
            created_at=get_now()
        )
        cursor.execute(
            """
        INSERT INTO
            {schema}.{table_name} ({fields})
        VALUES
            ({placeholders})
        """.format(
            schema=DB_CONFIG.schema,
            table_name=DB_CONFIG.query_table_name,
            fields=', '.join(data_to_insert.keys()),
            placeholders=', '.join(['%s'] * len(data_to_insert))
        ),
            tuple(data_to_insert.values())
        )
        conn.commit()
        conn.close()
