import pickle as pkl
import pandas as pd
import numpy as np
from glob import glob
from graph_helpers import load_graph_by_name
from helpers import infected_nodes, cascade_source
from collections import Counter

graph = 'grqc'
model = 'ic'
# suffix = '_tmp'
# cascade_fraction = 0
# suffix = '_s0.01'
cascade_fraction = 0.02
obs_frac = "leaves"

dirname = 'cascade-weighted/{}-m{}-s{}-o{}/*'.format(graph, model, cascade_fraction, obs_frac)

g = load_graph_by_name(graph, weighted=True)

gprop = g.graph_properties
p_min, p_max = gprop['p_min'], gprop['p_max']
print('p_min={}, p_max={}'.format(p_min, p_max))

os = [pkl.load(open(p, 'rb'))[0] for p in glob(dirname)]
cs = [pkl.load(open(p, 'rb'))[1] for p in glob(dirname)]
obs_sizes = [len(o) for o in os]
c_sizes = [len(infected_nodes(c)) for c in cs]
roots = list(map(cascade_source, cs))
print('roots freq:')
print(Counter(roots).most_common(10))

cascasdes = Counter([tuple(infected_nodes(c)) for c in cs])
print('top cascade freq:')
for _, c in Counter(cascasdes).most_common(10):
    print('freq:', c)

print('cascade size describe:')
print(pd.Series(c_sizes).describe())
print('-' * 10)
print('fraction', np.mean(c_sizes) / g.num_vertices())

print('-' * 10)
print('obs_sizes describe:')
print(pd.Series(obs_sizes).describe())

