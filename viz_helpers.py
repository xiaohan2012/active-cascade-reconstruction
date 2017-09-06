import numpy as np


def lattice_node_pos(g, shape):
    pos = g.new_vertex_property('vector<float>')
    for v in g.vertices():
        r, c = int(int(v) / shape[1]), int(v) % shape[1]
        pos[v] = np.array([r, c])
    return pos
