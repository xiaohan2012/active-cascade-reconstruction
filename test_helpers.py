from graph_helpers import has_vertex


def check_tree_samples(qs, c, trees):
    # make sure the tree sampels are updated
    # exclude the last query
    for q in qs[:-1]:
        for t in trees:
            if c[q] >= 0:
                if isinstance(t, set):
                    assert q in t
                else:
                    assert has_vertex(t, q)
            else:
                if isinstance(t, set):
                    assert q not in t
                else:
                    assert not has_vertex(t, q)


def check_error_esitmator(qs, c, est):
    # make sure the tree sampels are updated
    # exclude the last query
    for q in qs[:-1]:
        if c[q] >= 0:
            # infected
            assert est._m[q, :].sum() == est.n_col
        else:
            # uninfected
            assert est._m[q, :].sum() == 0
    assert (est.n_row, est.n_col) == est._m.shape
