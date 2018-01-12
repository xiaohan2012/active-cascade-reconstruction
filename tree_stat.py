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
        # print('invalid_tree_indices', invalid_tree_indices)
        for i, t in zip(invalid_tree_indices, trees):
            self._m[:, i] = False
            for v in t:
                self._m[v, i] = True

    def count(self, query, condition, targets, return_denum=False):
        mask = (self._m[query, :] == condition).nonzero()[0]
        # print('mask', mask)
        # print('np.asarray(targets)[:, None]', np.array(list(targets))[:, None])
        sub_m = self._m[np.asarray(list(targets))[:, None], mask]
        if not return_denum:
            return sub_m.sum(axis=1)
        else:
            return sub_m.sum(axis=1), len(mask)

    def proba(self, *args, **kwargs):
        num, denum = self.count(*args, **kwargs, return_denum=True)
        return num / denum

    def _remove_extreme_vals(self, v):
        # remove zero and one
        return v[(v != 0) & (v != 1)]

    def _sum_entropy(self, p):
        return -(p * np.log(p) + (1-p) * np.log(1-p)).sum()

    def prediction_error(self, query, condition, targets):
        p = self.proba(query, condition, targets)
        p = self._remove_extreme_vals(p)
        return self._sum_entropy(p)

    def query_score(self, query, targets):
        num0, denum0 = self.count(query, 0, targets, return_denum=True)
        num1, denum1 = self.count(query, 1, targets, return_denum=True)

        p0, p1 = (self._remove_extreme_vals(num0 / denum0),
                  self._remove_extreme_vals(num1 / denum1))

        weights = np.array([denum0, denum1]) / self.n_col
        errors = np.array([self._sum_entropy(p0), self._sum_entropy(p1)])
        return (weights * errors).sum()
