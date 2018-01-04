from core import sample_steiner_trees
from graph_helpers import has_vertex
from core1 import matching_trees


class TreeSamplePool():
    def __init__(self, g, n_samples, method, gi=None,
                 return_tree_nodes=True):
        self.g = g
        self.n_samples = n_samples
        self.gi = gi
        self.method = method
        self.return_tree_nodes = return_tree_nodes
        self._samples = []

    def fill(self, obs):
        self._samples = sample_steiner_trees(
            self.g, obs,
            method=self.method,
            n_samples=self.n_samples,
            return_tree_nodes=self.return_tree_nodes,
            gi=self.gi)

        # self._tree_nodes_samples = [set(extract_nodes(t))
        #                             for t in self._samples]

    def update_samples(self, inf_nodes, node, label):
        """if label=1, assuming `inf_nodes` includes `node` already
        if label=0, assuming `self.g` removes `node` already
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
            gi=self.gi)
        
        self._samples = valid_samples + new_samples
        # self._tree_nodes_samples = valid_tree_nodes + [set(extract_nodes(t))
        #                                                for t in new_samples]

    @property
    def samples(self):
        return self._samples

    @property
    def is_empty(self):
        return len(self._samples) == 0
