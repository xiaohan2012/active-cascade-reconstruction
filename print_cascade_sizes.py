import pickle as pkl
import numpy as np
from glob import glob
from graph_helpers import load_graph_by_name
from helpers import infected_nodes

graph = 'lattice-1024'
model = 'si'

if model == 'ic':
    dirname = 'cascade-weighted/{}-m{}-o0.1/*'.format(graph, model)
else:
    stop_fraction = 0.15
    dirname = 'cascade-weighted/{}-m{}-s{}-o0.1/*'.format(graph, model, stop_fraction)

g = load_graph_by_name(graph, weighted=True)
os = [pkl.load(open(p, 'rb'))[0] for p in glob(dirname)]
cs = [pkl.load(open(p, 'rb'))[1] for p in glob(dirname)]
obs_sizes = [len(o) for o in os]
c_sizes = [len(infected_nodes(c)) for c in cs]
print(c_sizes)
print('mean cascade size:', np.mean(c_sizes))
print('fraction', np.mean(c_sizes) / g.num_vertices())
