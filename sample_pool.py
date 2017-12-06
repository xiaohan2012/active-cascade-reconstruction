from core import sample_steiner_trees


class TreeSamplePool():
    def __init__(self, g, obs, n_samples):
        self.tree_samples = sample_steiner_trees(
            g, obs,
            n_samples=n_samples)
        
        self.nodes_samples = None

    def update(self, g, infs, node, label):
        pass

    
