import line_profiler

import numpy as np
from sample_pool import TreeSamplePool
from random_steiner_tree.util import from_gt
from graph_helpers import remove_filters
from core1 import query_score, prediction_error
from graph_tool.generation import lattice


g = lattice((10, 10))
gv = remove_filters(g)
gi = from_gt(g)
pool = TreeSamplePool(gv,
                      n_samples=20,
                      method='cut',
                      gi=gi,
                      return_tree_nodes=True  # using tree nodes
)

n_obs = 10
obs = np.random.permutation(g.num_vertices())[:n_obs]

print(obs)
pool.fill(obs)

q = 0
hidden_nodes = set(map(int, g.vertices())) - {q}

# profile = line_profiler.LineProfiler(query_score)
# profile.runcall(query_score, q, pool.samples, hidden_nodes)
# profile.print_stats()


profile = line_profiler.LineProfiler(prediction_error)
profile.runcall(prediction_error, q, 1, pool.samples, hidden_nodes)
profile.print_stats()
