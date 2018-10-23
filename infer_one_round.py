# coding: utf-8

import os
import time
import pickle as pkl
import argparse
from tqdm import tqdm

from helpers import (
    cascade_source,
    makedir_if_not_there,
    timeout,
    init_db
)
from inference import infection_probability
from graph_helpers import (
    load_graph_by_name,
    remove_filters,
    observe_uninfected_node,
    get_edge_weights
)
from sample_pool import (
    TreeSamplePool,
    SimulatedCascadePool
)
from random_steiner_tree.util import (
    from_gt,
    isolate_vertex
)
from tree_stat import TreeBasedStatistics
from root_sampler import (
    build_root_sampler_by_pagerank_score,
    build_true_root_sampler
)
from arg_helpers import (
    add_cascade_parameter_args
)
from helpers import (
    get_query_result,
    get_inference_result,
    get_now
)
from config import INFER_TIMEOUT, DB_CONFIG


def infer_probas_from_queries(
        g,
        obs,
        c,
        queries,
        sampling_method,
        root_sampler_name,
        n_samples,
        every=1,
        iter_callback=None,
        verbose=False,
        sampler_kwargs={},
):
    n_nodes = g.num_vertices()

    assert root_sampler_name in {'random', 'pagerank', 'true_root'}

    if root_sampler_name == 'pagerank':
        root_sampler = build_root_sampler_by_pagerank_score(g, obs, c)
    elif root_sampler_name == 'true_root':
        root_sampler = build_true_root_sampler(c)
    else:
        root_sampler = None

    g = remove_filters(g)
    weights = get_edge_weights(g)
    gi = from_gt(g, weights=weights)

    obs_inf = set(obs)
    obs_uninf = set()
    
    probas_list = []

    if sampling_method == 'simulation':
        sampler = SimulatedCascadePool(
            g,
            n_samples,
            cascade_params=sampler_kwargs
        )
    else:
        sampler = TreeSamplePool(
            g, n_samples=n_samples,
            method=sampling_method,
            gi=gi,
            with_resampling=False,
            return_type='nodes'
        )
    
    estimator = TreeBasedStatistics(g)
    sampler.fill(
        obs,
        root_sampler=root_sampler
    )
    estimator.build_matrix(sampler.samples)

    # initial step (without any queries)
    probas = infection_probability(g, obs_inf, sampler, error_estimator=estimator)
    probas_list.append(probas)

    if verbose:
        qs_iter = tqdm(queries)
    else:
        qs_iter = queries
    for i_iter, q in enumerate(qs_iter):
        if c[q] >= 0:  # infected
            obs_inf |= {q}
        else:
            observe_uninfected_node(g, q, obs_inf)
            isolate_vertex(gi, q)
            obs_uninf |= {q}
            # print('g.num_vertices()', g.num_vertices())

        # update samples
        label = int(c[q] >= 0)
        if root_sampler_name == 'pagerank':
            try:
                root_sampler = build_root_sampler_by_pagerank_score(g, obs_inf, c)
            except ValueError:
                print('pagerank score for root_sampler all zero, break')
                break

        if i_iter % every == 0:
            # print('i_iter', i_iter)
            if i_iter == 0:
                node_update_info = {q: label}
            else:
                node_update_info[q] = label

            # evaluate every `every` iteration
            new_samples = sampler.update_samples(obs_inf,
                                                 node_update_info,
                                                 root_sampler=root_sampler,
                                                 log=False,
                                                 verbose=False)
            estimator.update_trees(new_samples, node_update_info)

            # new probas
            probas = infection_probability(g, obs_inf, sampler, error_estimator=estimator)

            # make sure data dimension does not change
            assert len(probas) == n_nodes
            assert g.num_vertices() == n_nodes, '{} != {}'.format(g.num_vertices(), n_nodes)

            probas_list.append(probas)

            # refresh it
            node_update_info = {}

            if callable(iter_callback):
                iter_callback(g, sampler, estimator, obs_inf, obs_uninf)

        else:
            # accumulate info
            node_update_info[q] = label

    return probas_list, sampler, estimator


@timeout(seconds=INFER_TIMEOUT)
def one_round(
        g,
        obs,
        c,
        cascade_path,
        queries,
        n_samples=100,
        every=1,
        sampling_method='loop_erased',
        debug=False,
        verbose=False,
        args=None
):
    stime = time.time()

    if sampling_method == 'simulation':
        sampler_kwargs = dict(
            p=args.infection_proba,
            stop_fraction=args.cascade_size,
            source=cascade_source(c),
            cascade_model=args.cascade_model,
            debug=debug
        )
    else:
        sampler_kwargs = dict()

    # infer the infection probability
    probas_list, _, _ = infer_probas_from_queries(
        g, obs, c, queries,
        sampling_method,
        root_sampler_name='true_root',
        n_samples=n_samples,
        every=every,
        verbose=verbose,
        sampler_kwargs=sampler_kwargs
    )

    time_elapsed = time.time() - stime
    return dict(
        probas=probas_list,
        time_cost=time_elapsed
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-g', '--graph',
                        help='graph name')
    parser.add_argument('-f', '--graph_suffix', required=True,
                        help='suffix of graph name')
    parser.add_argument('--dataset', required=True,
                        help='dataset name')

    # query method related
    parser.add_argument('--query_method',
                        help='query method used for infer hidden infections')
    parser.add_argument('--n_queries', default=10, type=int,
                        help='number of queries')
    parser.add_argument('--query_sampling_method', default='loop_erased', type=str,
                        choices={'loop_erased', 'cut', 'cut_naive', 'simulation'},
                        help='the steiner tree sampling method')
    parser.add_argument('--root_sampler', type=str,
                        default='pagerank',
                        choices={'pagerank', 'random', 'true_root'},
                        help='the steiner tree sampling method')
    parser.add_argument('--query_n_samples', default=100, type=int,
                        help='number of samples')
    parser.add_argument('--min_proba', default=0.0, type=float,
                        help='(minimum) threshold used for pruning candidate nodes')

    # cascade related
    parser.add_argument('-c', '--cascade_path',
                        help='directory to read cascades')
    add_cascade_parameter_args(parser)
    
    # inference related
    parser.add_argument('--sampling_method',
                        default='simulation',
                        choices=('loop_erased', 'cut', 'simulation'),
                        help='')    
    parser.add_argument('-s', '--n_samples', type=int,
                        default=100,
                        help='number of samples')
    
    parser.add_argument('--infer_every',
                        default=1,
                        type=int,
                        help='evaluate every ?')
    parser.add_argument('--debug',
                        action='store_true',
                        help='')
    parser.add_argument('--verbose',
                        action='store_true',
                        help='')

    args = parser.parse_args()

    print("Args:")
    print('-' * 10)
    for k, v in args._get_kwargs():
        print("{}={}".format(k, v))

    graph_name = args.graph
    graph_suffix = args.graph_suffix
    n_samples = args.n_samples


    g = load_graph_by_name(
        graph_name, weighted=False,
        suffix=graph_suffix
    )

    obs, c = pkl.load(open(args.cascade_path, 'rb'))

    c_id = int(os.path.basename(args.cascade_path).split('.')[0])
    
    # load the queries
    conn, cursor = init_db(args.debug)

    inf_result = get_inference_result(
        cursor,
        args.dataset,
        c_id,
        args.query_method,
        args.query_sampling_method,
        args.query_n_samples,
        args.n_queries,
        args.root_sampler,
        args.min_proba,
        args.sampling_method,
        args.n_samples,
        args.infer_every
    )
    if inf_result is not None:
        print("inference processed already, skip")
        conn.close()
    else:        
        query_result = get_query_result(
            cursor,
            args.dataset,
            c_id,
            args.query_method,
            args.query_sampling_method,
            args.query_n_samples,
            args.n_queries,
            args.root_sampler,
            args.min_proba,
            fields=['queries']
        )
        if query_result is None:
            raise IOError('row not available')
        
        queries = pkl.loads(query_result[0])[0]

        output = one_round(
            g,
            obs,
            c,
            args.cascade_path,
            queries,
            n_samples=n_samples,
            every=args.infer_every,
            sampling_method=args.sampling_method,
            verbose=args.verbose,
            args=args
        )


        probas, time_cost = output['probas'], output['time_cost']

        data_to_insert = dict(
            dataset=args.dataset,
            cascade_id=c_id,
            query_method=args.query_method,
            query_sampling_method=args.query_sampling_method,
            query_n_samples=args.query_n_samples,
            n_queries=args.n_queries,
            root_sampler=args.root_sampler,
            pruning_proba=args.min_proba,
            infer_sampling_method=args.sampling_method,
            infer_n_samples=args.n_samples,
            every=args.infer_every,
            probas=pkl.dumps(probas),
            time_elapsed=time_cost,
            created_at=get_now()
        )
        cursor.execute(
            """
        INSERT INTO
            {table_name} ({fields})
        VALUES
            ({placeholders})
        """.format(
            table_name=DB_CONFIG.inference_table_name,
            fields=', '.join(data_to_insert.keys()),
            placeholders=', '.join(['?'] * len(data_to_insert))
        ),
            tuple(data_to_insert.values())
        )
        conn.commit()
        conn.close()
