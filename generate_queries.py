# coding: utf-8

import pickle as pkl
import glob
import os
from tqdm import tqdm


from query_selection import (RandomQueryGenerator, EntropyQueryGenerator,
                             PRQueryGenerator, PredictionErrorQueryGenerator)
from simulator import Simulator
from joblib import Parallel, delayed
from graph_helpers import remove_filters, load_graph_by_name


def load_cascades(dirname):
    for p in glob.glob(dirname+'/*.pkl'):
        yield p, pkl.load(open(p, 'rb'))


graph_name = 'dolphin'
n_queries = 10
n_samples = 100
output_dir = 'outputs/queries/{}'.format(graph_name)


g = load_graph_by_name(graph_name)


strategies = [
    (RandomQueryGenerator, {}, 'random'),
    (PRQueryGenerator, {}, 'pagerank'),
    (EntropyQueryGenerator, {'num_stt': n_samples, 'method': 'entropy', 'use_resample': False}, 'entropy'),
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
    
cascade_generator = load_cascades('cascade/{}/'.format(graph_name))


# run!
Parallel(n_jobs=-1)(delayed(one_round)(g, obs, c, path, cls, param, name, output_dir)
                    for path, (obs, c) in tqdm(cascade_generator)
                    for cls, param, name in strategies)
        

