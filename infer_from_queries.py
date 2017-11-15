# coding: utf-8


import os
import pickle as pkl
import argparse
from helpers import load_cascades
from inference import infection_probability
from graph_helpers import (load_graph_by_name, remove_filters,
                           observe_uninfected_node)
from tqdm import tqdm
from joblib import Parallel, delayed


parser = argparse.ArgumentParser(description='')
parser.add_argument('-g', '--graph', help='graph name')
parser.add_argument('-s', '--n_samples', default=100, help='number of samples')

args = parser.parse_args()

graph_name = args.graph
n_samples = args.n_samples

query_dirname = 'outputs/queries/'
inf_proba_dirname = 'outputs/inf_probas'


g = load_graph_by_name(graph_name)

cascades = load_cascades('cascade/' + graph_name)


methods = ['pagerank', 'random', 'entropy', 'prediction_error']


def one_round(g, obs, c, c_path, method, query_dirname, inf_proba_dirname):
    g = remove_filters(g)
    obs_inf = set(obs)
    # loop
    cid = os.path.basename(c_path).split('.')[0]
    query_log_path = os.path.join(query_dirname, graph_name, method, '{}.pkl'.format(cid))
    queries, _ = pkl.load(open(query_log_path, 'rb'))

    probas_list = []
    for q in queries:
        if c[q] >= 0:  # infected
            obs_inf |= {q}
        else:
            observe_uninfected_node(g, q, obs_inf)
            # isolate_node(g, q)
            # hide_disconnected_components(g, obs_inf)
        
        probas = infection_probability(g, obs_inf, n_samples=n_samples)
        probas_list.append(probas)

    probas_dir = os.path.join(inf_proba_dirname, graph_name, method)
    if not os.path.exists(probas_dir):
        os.makedirs(probas_dir)
    path = os.path.join(probas_dir, '{}.pkl'.format(cid))
    pkl.dump(probas_list, open(path, 'wb'))


Parallel(n_jobs=-1)(delayed(one_round)(g, obs, c, path, method, query_dirname, inf_proba_dirname)
                    for path, (obs, c) in tqdm(cascades)
                    for method in methods)
