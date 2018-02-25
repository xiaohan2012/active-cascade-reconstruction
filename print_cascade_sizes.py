import pickle as pkl
import numpy as np
from glob import glob
from graph_helpers import load_graph_by_name
from helpers import infected_nodes

g = load_graph_by_name('grqc', weighted=True)
os = [pkl.load(open(p, 'rb'))[0] for p in glob('cascade-weighted/grqc-mic-o0.1/*')]
cs = [pkl.load(open(p, 'rb'))[1] for p in glob('cascade-weighted/grqc-mic-o0.1/*')]
obs_sizes = [len(o) for o in os]
c_sizes = [len(infected_nodes(c)) for c in cs]
print('mean cascade size:', np.mean(c_sizes))
