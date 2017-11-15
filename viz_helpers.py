import numpy as np
import matplotlib

from inference import infection_probability
from graph_tool.draw import graph_draw
from graph_helpers import (extract_nodes,
                           observe_uninfected_node,
                           remove_filters)


def lattice_node_pos(g, shape):
    pos = g.new_vertex_property('vector<float>')
    for v in g.vertices():
        r, c = int(int(v) / shape[1]), int(v) % shape[1]
        pos[v] = np.array([r, c])
    return pos


OBS, QUERY, DEFAULT = range(3)

SIZE_ZERO = 0
SIZE_SMALL = 10
SIZE_MEDIUM = 20
SIZE_LARGE = 30

SHAPE_CIRCLE = 'circle'
SHAPE_PENTAGON = 'pentagon'
SHAPE_HEXAGON = 'hexagon'
SHAPE_SQUARE = 'square'
SHAPE_TRIANGLE = 'triangle'


class QueryIllustrator():
    """illustrate the querying process"""

    def __init__(self, g, obs, c,
                 pos,
                 output_size=(300, 300),
                 vertex_size=20,
                 vcmap=matplotlib.cm.Reds):
        self.g_bak = g
        self.g = remove_filters(g)  # refresh
        self.obs = obs
        self.c = c

        self.pos = pos
        self.output_size = output_size
        self.vertex_size = vertex_size
        self.vcmap = vcmap
        
        self.inf_nodes = set((self.c >= 0).nonzero()[0])
        
        self.obs_inf = set(self.obs)
        self.obs_uninf = set()
        self.hidden_inf = self.inf_nodes - self.obs_inf
        self.hidden_uninf = set(extract_nodes(g)) - self.inf_nodes
        
    def add_query(self, query):
        if self.c[query] >= 0:  # infected
            self.obs_inf |= {query}
            self.hidden_inf -= {query}
        else:
            self.obs_uninf |= {query}
            self.hidden_uninf -= {query}
            observe_uninfected_node(self.g, query, self.obs_inf)

    def plot_snapshot(self, query, n_samples, ax=None):
        """plot one snap shot using one query and update node infection/observailability
        n_samples: num of samples used for inference
        """
        self.add_query(query)
        probas = infection_probability(self.g, self.obs_inf, n_samples=n_samples)
        # print(probas.shape)
        vcolor = self.node_colors(probas)
        vcolor[query] = 1  # highlight query

        vshape = self.node_shapes(query)
        vshape[query] = SHAPE_PENTAGON  # hack, override it

        graph_draw(self.g_bak,  # use the very earliest graph
                   pos=self.pos,
                   vcmap=self.vcmap,
                   output_size=self.output_size,
                   vertex_size=self.vertex_size,
                   vertex_fill_color=vcolor,
                   vertex_shape=vshape,
                   mplfig=ax)
        
    def node_properties_by_group(self, g, value_groups, dtype, default_val):
        """
        value_groups: dict of (dtype, list): (value, list of nodes)
        """
        vprop = g.new_vertex_property(dtype)
        vprop.set_value(default_val)
        for val, grp in value_groups:
            for i in grp:
                vprop[i] = val
        return vprop

    def node_shapes(self, query):
        groups = [(SHAPE_PENTAGON, [query]),
                  (SHAPE_SQUARE, self.obs_inf | self.obs_uninf),
                  (SHAPE_CIRCLE, self.hidden_inf),
                  (SHAPE_TRIANGLE, self.hidden_uninf)]
        return self.node_properties_by_group(self.g_bak, groups, 'string', SHAPE_CIRCLE)

    def node_colors(self, probas):
        color = self.g_bak.new_vertex_property('float')
        assert len(probas) == len(color.a)
        color.a = probas

        # might be fewer vertices in g than g_bak
        # because of vertex removal
        # for v, proba in zip(self.g.vertices(), probas):
        #     color[v] = proba
        return color


class InfectionProbability():
    def __init__(self, g,
                 pos,
                 output_size=(300, 300),
                 vertex_size=20,
                 vcmap=matplotlib.cm.Reds):
        self.g = g
        self.pos = pos
        self.output_size = output_size
        self.vertex_size = vertex_size
        self.vcmap = vcmap

    def plot(self, obs, ax=None, **kwargs):
        """kwargs: refer to `inference.infection_probability`"""
        inf_probas = infection_probability(self.g, obs, **kwargs)
        vcolor = self.g.new_vertex_property('float')
        vcolor.set_value(0)
        vcolor.a = inf_probas

        vshape = self.g.new_vertex_property('string')
        vshape.set_value('circle')

        for o in obs:
            vcolor[o] = 0
            vshape[o] = 'square'

        graph_draw(self.g,
                   pos=self.pos,
                   vcmap=self.vcmap,
                   output_size=self.output_size,
                   vertex_size=self.vertex_size,
                   vertex_fill_color=vcolor,
                   vertex_shape=vshape,
                   mplfig=ax)
