import os
import pickle
import argparse
from graph_helpers import load_graph_by_name
from experiment import gen_input
from tqdm import tqdm

parser = argparse.ArgumentParser(description='')
parser.add_argument('-g', '--graph', required=True, help='graph name')
parser.add_argument('-n', '--n_cascades', type=int, default=100,
                    help='number of cascades')
parser.add_argument('-o', '--obs_fraction', type=float, default=0.2,
                    help='fraction of observed  nodes')
parser.add_argument('-d', '--output_dir', default='cascade',
                    help='output directory')

# the following applicable to real cascades
parser.add_argument('-c', '--cascade_path',
                    help='cascade path (applicable if the cascade is given)')

# the following applicable to simulated cascades
parser.add_argument('-m', '--cascade_model', type=str, default='si',
                    choices=('si', 'ic'),
                    help='cascade model')
parser.add_argument('-s', '--stop_fraction', type=float, default=0.5,
                    help='fraction of infected nodes to stop')
parser.add_argument('-p', '--infection_proba', type=float, default=0.5,
                    help='infection probability')
parser.add_argument('--min_size', type=int, default=10,
                    help='minimum cascade size (applicable for IC model)')
parser.add_argument('-r', '--use_edge_weights', action='store_true',
                    help="""flag on using random edge probability.
If ON, edge weight is sampled uniformly from [p_min, p_max]""")


args = parser.parse_args()
graph_name = args.graph

if not args.use_edge_weights:
    print('uniform edge weight')
    g = load_graph_by_name(graph_name, weighted=False)
    p = args.infection_proba
else:
    print('non-uniform edge weight')
    g = load_graph_by_name(graph_name, weighted=True)
    p = g.edge_properties['weights'].a

print('p=', p)

for i in tqdm(range(args.n_cascades)):
    obs, c = gen_input(g,
                       cascade_path=args.cascade_path,
                       stop_fraction=args.stop_fraction,
                       q=args.obs_fraction,
                       p=p,
                       model=args.cascade_model,
                       min_size=args.min_size)

    # d = os.path.join(args.output_dir, graph_name)
    d = args.output_dir
    if not os.path.exists(d):
        os.makedirs(d)
    path = os.path.join(d, '{}.pkl'.format(i))
    pickle.dump((obs, c), open(path, 'wb'))
