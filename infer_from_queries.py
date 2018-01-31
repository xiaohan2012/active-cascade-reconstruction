# coding: utf-8

import os
import time
import pickle as pkl
import argparse
from tqdm import tqdm
from joblib import Parallel, delayed

from helpers import load_cascades
from inference import infection_probability
from graph_helpers import (load_graph_by_name, remove_filters,
                           observe_uninfected_node)
from sample_pool import TreeSamplePool
from random_steiner_tree.util import from_gt, isolate_vertex
from tree_stat import TreeBasedStatistics
from root_sampler import build_root_sampler_by_pagerank_score
from sdm2018 import find_tree_greedy
from sdm2018.utils import earliest_obs_node


def infer_infections_by_order_steiner_tree(g, obs, c, queries):
    g = remove_filters(g)
    obs_inf = set(obs)
    list_of_infections = []
    for i, q in enumerate(queries):
        if c[q] >= 0:  # infected
            obs_inf |= {q}
        else:
            observe_uninfected_node(g, q, obs_inf)

        root = earliest_obs_node(obs, c)
        try:
            tree_nodes = find_tree_greedy(
                g, root, c, source=None, obs_nodes=obs_inf,
                return_nodes=True,
                debug=False,
                verbose=False
            )
        except AssertionError:
            print("{}th query raises AssertionError".format(i))
            break
        list_of_infections.append(tree_nodes - set(obs))
    return list_of_infections
    

def infer_probas_from_queries(g, obs, c, queries,
                              sampling_method, root_sampler_name, n_samples,
                              verbose=False):
    assert root_sampler_name in {None, 'pagerank'}

    if root_sampler_name == 'pagerank':
        root_sampler = build_root_sampler_by_pagerank_score(g, obs, c)
    else:
        root_sampler = None
        
    g = remove_filters(g)
    gi = from_gt(g)
    obs_inf = set(obs)
    probas_list = []

    sampler = TreeSamplePool(g, n_samples=n_samples,
                             method=sampling_method,
                             gi=gi,
                             return_tree_nodes=True)
    estimator = TreeBasedStatistics(g)
    sampler.fill(obs,
                 root_sampler=root_sampler)
    estimator.build_matrix(sampler.samples)

    if verbose:
        qs_iter = tqdm(queries)
    else:
        qs_iter = queries
    for q in qs_iter:
        if c[q] >= 0:  # infected
            obs_inf |= {q}
        else:
            observe_uninfected_node(g, q, obs_inf)
            isolate_vertex(gi, q)

        # update samples
        label = int(c[q] >= 0)
        if root_sampler_name == 'pagerank':
            root_sampler = build_root_sampler_by_pagerank_score(g, obs_inf, c)
            
        new_samples = sampler.update_samples(obs_inf, q, label, root_sampler=root_sampler)
        estimator.update_trees(new_samples, q, label)

        # new probas
        probas = infection_probability(g, obs_inf, sampler, error_estimator=estimator)
        probas_list.append(probas)

    return probas_list, sampler, estimator


def one_round(g, obs, c, c_path,
              query_method,
              inference_method,
              query_dirname, inf_proba_dirname,
              n_samples=250,
              root_sampler=None,
              sampling_method='loop_erased',
              debug=False,
              verbose=False):
    print('\nprocessing {} started, query_method={}, root_sampler={}, \n'.format(
        c_path, query_method, root_sampler))
    stime = time.time()
    
    cid = os.path.basename(c_path).split('.')[0]
    probas_dir = os.path.join(inf_proba_dirname, query_method)
    if not os.path.exists(probas_dir):
        os.makedirs(probas_dir)
    path = os.path.join(probas_dir, '{}.pkl'.format(cid))

    if os.path.exists(path):
        print('{} computed'.format(path))
        return
    
    query_log_path = os.path.join(query_dirname, query_method, '{}.pkl'.format(cid))
    queries, _ = pkl.load(open(query_log_path, 'rb'))

    if inference_method == 'inf_probas':
        # the real part
        probas_list, _, _ = infer_probas_from_queries(g, obs, c, queries,
                                                      sampling_method,
                                                      root_sampler,
                                                      n_samples,
                                                      verbose=verbose)
        pkl.dump(probas_list, open(path, 'wb'))
    elif inference_method == 'order_steiner_tree':
        hidden_infections = infer_infections_by_order_steiner_tree(g, obs, c, queries)
        pkl.dump(hidden_infections, open(path, 'wb'))
    else:
        raise ValueError('unknown inference method "{}"'.format(inference_method))

    print('\nprocessing {} done (query_method={}, inference_method={}): taking {:.4f} secs\n'.format(
        c_path,
        query_method, inference_method,
        time.time() - stime))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-g', '--graph',
                        help='graph name')
    parser.add_argument('-s', '--n_samples', type=int,
                        default=100,
                        help='number of samples')
    parser.add_argument('-m', '--inference_method',
                        default='inf_probas',
                        choices=('inf_probas', 'order_steiner_tree'),
                        help='method used for infer hidden infections')
    parser.add_argument('--query_method',
                        help='query method used for infer hidden infections')
    parser.add_argument('-r', '--root_sampler', type=str,
                        default='pagerank',
                        choices={'pagerank', None},
                        help='the steiner tree sampling method')

    parser.add_argument('-c', '--cascade_dir',
                        help='directory to read cascades')
    parser.add_argument('-q', '--query_dirname',
                        required=True,
                        help='directory of queries')
    parser.add_argument('-p', '--inf_proba_dirname',
                        required=True,
                        help='directory to store the inferred probabilities')
    parser.add_argument('--debug',
                        action='store_true',
                        help='')
    parser.add_argument('--verbose',
                        action='store_true',
                        help='')
    
    args = parser.parse_args()

    graph_name = args.graph
    n_samples = args.n_samples

    query_dirname = args.query_dirname
    inf_proba_dirname = args.inf_proba_dirname

    g = load_graph_by_name(graph_name)

    cascades = load_cascades(args.cascade_dir)

    if not args.debug:
        Parallel(n_jobs=-1)(delayed(one_round)(g, obs, c, path, args.query_method,
                                               args.inference_method,
                                               query_dirname,
                                               inf_proba_dirname, n_samples=n_samples,
                                               root_sampler=args.root_sampler,
                                               verbose=args.verbose)
                            for path, (obs, c) in tqdm(cascades))
    else:
        for path, (obs, c) in tqdm(cascades):
            one_round(g, obs, c, path, args.query_method,
                      args.inference_method,
                      query_dirname,
                      inf_proba_dirname, n_samples=n_samples,
                      root_sampler=args.root_sampler,
                      verbose=args.verbose)
