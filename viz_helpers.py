import seaborn as sns
import numpy as np
import matplotlib

from inference import infection_probability
from graph_tool.draw import graph_draw
from matplotlib.colors import ListedColormap


def lattice_node_pos(g, shape):
    pos = g.new_vertex_property('vector<float>')
    for v in g.vertices():
        r, c = int(int(v) / shape[1]), int(v) % shape[1]
        pos[v] = np.array([r, c])
    return pos


class QueryIllustrator():
    """illustrate the querying process"""

    OBS, QUERY, CORRECT, FP, FN, DEFAULT = range(6)

    SIZE_ZERO = 0
    SIZE_SMALL = 10
    SIZE_MEDIUM = 20
    SIZE_LARGE = 30

    SHAPE_CIRCLE = 'circle'
    SHAPE_PENTAGON = 'pentagon'
    SHAPE_HEXAGON = 'hexagon'
    SHAPE_SQUARE = 'square'
    SHAPE_TRIANGLE = 'triangle'
    
    @classmethod
    def colors(cls):
        colors = [""] * 6
        colors[cls.OBS] = 'pumpkin'
        colors[cls.QUERY] = "bright sky blue"
        colors[cls.CORRECT] = 'light green'
        colors[cls.FP] = 'salmon'
        colors[cls.FN] = 'grey'
        colors[cls.DEFAULT] = 'pale grey'
        return colors

    @classmethod
    def palette(cls):
        return sns.xkcd_palette(cls.colors())

    @classmethod
    def node_properties_by_group(cls, g, value_groups, dtype, default_val):
        """
        value_groups: dict of (dtype, list): (value, list of nodes)
        """
        vprop = g.new_vertex_property(dtype)
        vprop.set_value(default_val)
        for val, grp in value_groups:
            for i in grp:
                vprop[i] = val
        return vprop

    @classmethod
    def node_sizes(cls, g, obs, queries, correct, fp, fn):
        groups = [(cls.SIZE_SMALL, obs),
                  (cls.SIZE_LARGE, queries),
                  (cls.SIZE_MEDIUM, correct),
                  (cls.SIZE_MEDIUM, fp),
                  (cls.SIZE_MEDIUM, fn)]
        return cls.node_properties_by_group(g, groups, 'int', cls.SIZE_ZERO)

    @classmethod
    def node_shapes(cls, g, obs, queries, correct, fp, fn):
        groups = [(cls.SHAPE_CIRCLE, obs),
                  (cls.SHAPE_HEXAGON, queries),
                  (cls.SHAPE_CIRCLE, correct),
                  (cls.SHAPE_SQUARE, fp),
                  (cls.SHAPE_TRIANGLE, fn)]
        return cls.node_properties_by_group(g, groups, 'string', cls.SHAPE_CIRCLE)
    
    @classmethod
    def node_colors(cls, g, obs, queries, correct, fp, fn):
        groups = [(cls.OBS, obs),
                  (cls.QUERY, queries),
                  (cls.CORRECT, correct),
                  (cls.FP, fp),
                  (cls.FN, fn)]
        # prevent over-writing
        for v, grp in groups:
            if v in {cls.CORRECT, cls.FP, cls.FN}:
                grp -= set(queries)
        return cls.node_properties_by_group(g, groups, 'int', cls.DEFAULT)
       
    @classmethod
    def build_colormap(cls):
        return ListedColormap(cls.palette().as_hex())


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
