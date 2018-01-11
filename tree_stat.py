import numpy as np


class TreeBasedStatistics:
    def __init__(self, g, trees=None):
        self._g = g
        self.n_row = g.num_vertices()
        self.n_col = None
        self._m = None

        if trees is not None:
            self.build_matrix(trees)

    def build_matrix(self, trees):
        """trees: list of set of ints
        """
        self.n_row = self._g.num_vertices()
        self.n_col = len(trees)
        self._m = np.zeros((self.n_row, self.n_col), dtype=np.bool)
        for i, t in enumerate(trees):
            for v in t:
                self._m[v, i] = True

    def update_trees(self, trees, query, state):
        invalid_tree_indices = (self._m[query, :] != state).nonzero()[0]
        assert len(invalid_tree_indices) <= len(trees)  # need enough trees to update
        print('invalid_tree_indices', invalid_tree_indices)
        for i, t in zip(invalid_tree_indices, trees):
            self._m[:, i] = False
            for v in t:
                self._m[v, i] = True

    def count(self, query, condition, targets):
        mask = (self._m[query, :] == condition).nonzero()[0]
        sub_m = self._m[np.asarray(targets)[:, None], mask]
        return sub_m.sum(axis=1)

    def proba(self, *args, **kwargs):
        return self.count(*args, **kwargs) / self.n_col
