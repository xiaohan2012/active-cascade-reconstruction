import os
import pickle
import argparse
from graph_helpers import load_graph_by_name
from cascade_generator import gen_input
from tqdm import tqdm
from glob import glob


parser = argparse.ArgumentParser(description='')
parser.add_argument('-g', '--graph', required=True, help='graph name')
parser.add_argument('-f', '--graph_suffix', default='', help='suffix of graph path')

parser.add_argument('-n', '--n_cascades', type=int, default=12,
                    help='number of cascades')

parser.add_argument('-o', '--obs_fraction', type=float, default=0.2,
                    help='fraction of observed  nodes')
parser.add_argument('-d', '--output_dir', default='cascade',
                    help='output directory')

# the following applicable to simulated cascades
parser.add_argument('-m', '--cascade_model', type=str, default='si',
                    choices=('si', 'ic'),
                    help='cascade model')
parser.add_argument('-p', '--infection_proba', type=float, default=0.5,
                    help='infection probability')
parser.add_argument('--min_fraction', type=float, default=0.0,
                    help='minimum cascade size (applicable for IC model)')
parser.add_argument('--max_fraction', type=float, default=1.0,
                    help='maximum cascade size (applicable for IC model)')
parser.add_argument('-w', '--use_edge_weights', action='store_true',
                    help="""flag on using random edge probability.
If ON, edge weight is sampled uniformly from [p_min, p_max]""")

parser.add_argument('--observation_method', type=str, choices=('uniform', 'leaves', 'late',
                                                               'bfs-head', 'bfs-tail'),
                    help='how infections are observed')

parser.add_argument('-t', '--store_tree', action='store_true',
                    help="""store the tree or not""")

METHODS_WANT_TREE = {'leaves', 'bfs-head', 'bfs-tail'}

args = parser.parse_args()

print("Args:")
print('-' * 10)
for k, v in args._get_kwargs():
    print("{}={}".format(k, v))

graph_name = args.graph

g = load_graph_by_name(graph_name, weighted=False, suffix=args.graph_suffix)

if not args.use_edge_weights:
    print('use edge weights in cmd')
    p = args.infection_proba
else:
    print('use edge weights in graph')
    p = g.edge_properties['weights']

print('p=', p.a[:10])

root_sampler = lambda: None

d = args.output_dir
if not os.path.exists(d):
    os.makedirs(d)

for i in tqdm(range(args.n_cascades)):
    obs, c, tree = gen_input(
        g,
        source=root_sampler(),
        cascade_path=None,
        p=p,
        q=args.obs_fraction,
        model=args.cascade_model,
        observation_method=args.observation_method,
        min_fraction=args.min_fraction,
        max_fraction=args.max_fraction,
        return_tree=(args.observation_method in METHODS_WANT_TREE)
    )
    path = os.path.join(d, '{}.pkl'.format(i))

    if args.store_tree:
        pickle.dump((obs, c, tree), open(path, 'wb'))
    else:
        pickle.dump((obs, c), open(path, 'wb'))
