# cython: linetrace=True

import numpy as np
from libc.math cimport log


# @profile
cdef num_matching_trees(T, int node, int value):
    """
    Args:
    ---------
    T: list of set of ints, list of trees represented by nodes
    node: node to filter
    value: value to filter

    Returns:
    ---------
    int: number of matching trees
    """
    cdef int c = 0
    for t in T:
        if value == 1:
            if t.count(node):
                c += 1
        else:
            if t.count(node) == 0:
                c += 1
    return c
    # if value == 1:  # infected
    #     return len([t for t in T if node in t])
    # else:  # uninfected
    #     return len([t for t in T if node not in t])


cpdef matching_trees_cython(T, int node, int value):
    """
    T: list of set of ints, list of trees represented by nodes
    node: node to filter
    value: value to filter
    """
    if value == 1:  # infected
        # return [t for t in T if t.count(node)]
        return [t for t in T if node in t]
    else:  # uninfected
        # return [t for t in T if t.count(node) == 0]
        return [t for t in T if (node not in t)]

def matching_trees(T, node, value):
    """
    T: list of set of ints, list of trees represented by nodes
    node: node to filter
    value: value to filter
    """
    if value == 1:  # infected
        return [t for t in T if node in t]
    else:  # uninfected
        return [t for t in T if node not in t]

# @profile
cpdef prediction_error(int q, int y_hat, T, hidden_nodes):
    # filter T by (q, y_hat)
    sub_T = matching_trees_cython(T, q, y_hat)
    cdef double p, error = 0.0, N = len(sub_T)

    for u in hidden_nodes:
        try:
            p = len(matching_trees_cython(sub_T, u, 0)) / N
            if p == 0 or p == 1:
                raise ZeroDivisionError
            error -= (p * log(p) + (1-p) * log(1-p))
        except ZeroDivisionError:
            # entropy is zero
            pass

    return error

# @profile
def query_score(int q, T, hidden_nodes):
    assert q not in hidden_nodes
    cdef double p, score = 0
    if True:
        for y_hat in [0, 1]:
            p = len(matching_trees_cython(T, q, y_hat)) / len(T)
            score += p * prediction_error(q, y_hat, T, hidden_nodes)
            # if q in {0, 89, 99, 9}:  # debug
            # print('p(q={}, y={})={}'.format(q, y_hat, p))
    else:
        score += prediction_error(q, 1, T, hidden_nodes)
    return score
