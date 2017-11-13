import os
import pickle
import argparse
from graph_helpers import load_graph_by_name
from experiment import gen_input
from tqdm import tqdm

parser = argparse.ArgumentParser(description='')
parser.add_argument('-g', '--graph', help='graph name')
parser.add_argument('-n', '--n_cascades', default=100, help='number of cascades')
parser.add_argument('-s', '--stop_fraction', default=0.5, help='fraction of infected nodes to stop')
parser.add_argument('-o', '--obs_fraction', default=0.2, help='fraction of observed  nodes')
parser.add_argument('-p', '--infection_proba', default=0.5, help='infection probability')
parser.add_argument('-d', '--output_dir', default='cascade', help='output directory')

args = parser.parse_args()
graph_name = args.graph
g = load_graph_by_name(graph_name)

for i in tqdm(range(args.n_cascades)):
    obs, c = gen_input(g,
                       stop_fraction=args.stop_fraction,
                       q=args.obs_fraction,
                       p=args.infection_proba)

    d = os.path.join(args.output_dir, graph_name)
    if not os.path.exists(d):
        os.makedirs(d)
    path = os.path.join(d, '{}.pkl'.format(i))
    pickle.dump((obs, c), open(path, 'wb'))
