from core import sample_steiner_trees
from graph_helpers import has_vertex, extract_nodes
from core1 import matching_trees


class TreeSamplePool():
    def __init__(self, g, n_samples):
        self.g = g
        self.n_samples = n_samples
        self._tree_samples = []
        self._tree_nodes_samples = []

    def fill(self, obs):
        self._tree_samples = sample_steiner_trees(
            self.g, obs,
            n_samples=self.n_samples)
        self._tree_nodes_samples = [set(extract_nodes(t))
                                    for t in self._tree_samples]
    
    def update_samples(self, inf_nodes, node, label):
        """if label=1, assuming `inf_nodes` includes `node` already
        if label=0, assuming `self.g` removes `node` already
        """
        assert label in {0, 1}  # 0: uninfected, 1: infected
        if label == 1:
            assert node in inf_nodes

            def feasible(t):
                return has_vertex(t, node)
        else:
            def feasible(t):
                return not has_vertex(t, node)
            
        valid_trees = [t for t in self._tree_samples
                       if feasible(t)]

        valid_tree_nodes = matching_trees(self._tree_nodes_samples, node, label)

        new_samples = sample_steiner_trees(
            self.g, inf_nodes,
            n_samples=self.n_samples - len(valid_trees))
        
        self._tree_samples = valid_trees + new_samples
        self._tree_nodes_samples = valid_tree_nodes + [set(extract_nodes(t))
                                                      for t in new_samples]

    @property
    def tree_samples(self):
        return self._tree_samples

    @property
    def nodes_samples(self):
        return self._tree_nodes_samples

    @property
    def is_empty(self):
        return len(self.samples) == 0
