import numpy as np
from graph_tool import GraphView

from core import sample_steiner_trees
from graph_helpers import has_vertex
from core1 import matching_trees
from helpers import infected_nodes
from cascade_generator import incremental_simulation


class TreeSamplePool():
    def __init__(self, g, n_samples, method,
                 edge_weights=None,
                 gi=None,
                 with_inc_sampling=False,
                 return_tree_nodes=True):
        self.g = g
        self.num_nodes = g.num_vertices()  # fixed
        self.n_samples = n_samples
        self.edge_weights = edge_weights
        self.gi = gi
        self.method = method
        self.return_tree_nodes = return_tree_nodes
        self.with_inc_sampling = with_inc_sampling
        self._samples = []
        print('DEBUG: TreeSamplePool.with_inc_sampling=', self.with_inc_sampling)

    def fill(self, obs, **kwargs):
        self._samples = sample_steiner_trees(
            self.g, obs,
            method=self.method,
            n_samples=self.n_samples,
            return_tree_nodes=self.return_tree_nodes,
            gi=self.gi,
            **kwargs)

        if self.with_inc_sampling:
            self._samples = [self.add_incremental_edges(s)
                             for s in self._samples]

        # self._tree_nodes_samples = [set(extract_nodes(t))
        #                             for t in self._samples]

    def add_incremental_edges(self, tree_nodes):
        if isinstance(tree_nodes, GraphView):
            raise TypeError('add_incremental_edges does not support GraphView yet. ' +
                            'Please pass in a set of nodes')
        fake_c = np.ones(self.num_nodes) * (-1)
        fake_c[list(tree_nodes)] = 1
        # print('len(tree_nodes)', len(tree_nodes))
        assert self.edge_weights is not None, 'for incremental edge addition, edge weight should be given'
        new_c = incremental_simulation(self.g, fake_c, self.edge_weights,
                                       self.num_nodes,
                                       return_new_edges=False)
        # print('len(infected_nodes(new_c))', len(infected_nodes(new_c)))
        return set(infected_nodes(new_c))
        
    # @profile
    def update_samples(self, inf_nodes, node, label, **kwargs):
        """if label=1, assuming `inf_nodes` includes `node` already
        if label=0, assuming `self.g` removes `node` already
        
        Return:
        new_samples
        """
        assert label in {0, 1}  # 0: uninfected, 1: infected
        if not self.return_tree_nodes:
            # use tree
            if label == 1:
                assert node in inf_nodes

                def feasible(t):
                    return has_vertex(t, node)
            else:
                def feasible(t):
                    return not has_vertex(t, node)
                
            valid_samples = [t for t in self._samples
                             if feasible(t)]
        else:
            # use nodes
            valid_samples = matching_trees(self._samples, node, label)
            
        new_samples = sample_steiner_trees(
            self.g, inf_nodes,
            method=self.method,
            n_samples=self.n_samples - len(valid_samples),
            return_tree_nodes=self.return_tree_nodes,
            gi=self.gi,
            **kwargs)

        if self.with_inc_sampling:
            # print('With incremental sampling')
            new_samples = [self.add_incremental_edges(t)
                           for t in new_samples]
            
        self._samples = valid_samples + new_samples

        return new_samples

    @property
    def samples(self):
        return self._samples

    @property
    def is_empty(self):
        return len(self._samples) == 0
