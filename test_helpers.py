from graph_helpers import has_vertex


def check_tree_samples(qs, c, trees, every=1):
    # make sure the tree sampels are updated
    # exclude the last query
    for i, q in enumerate(qs[:-1]):
        if i % every == 0:
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


def check_error_esitmator(qs, c, est, every=1):
    # make sure the tree sampels are updated
    # exclude the last query
    for i, q in enumerate(qs[:-1]):
        if i % every == 0:
            if c[q] >= 0:
                # infected
                assert est._m[q, :].sum() == est.n_col
            else:
                # uninfected
                assert est._m[q, :].sum() == 0
    assert (est.n_row, est.n_col) == est._m.shape
