import pytest
import numpy as np
from numpy.testing import assert_array_equal as assert_eq_np
from graph_tool import Graph
from scipy.stats import entropy

from tree_stat import TreeBasedStatistics


@pytest.fixture
def trees():
    return [
        {2, 5},
        {0, 3},
        {0, 3, 4},
        {3, 4, 5},
        {0, 2, 3}
    ]


@pytest.fixture
def new_trees():
    return [
        {0, 1},
        {0, 4}
    ]


@pytest.fixture
def g():
    g = Graph(directed=False)
    g.add_vertex(6)
    return g


@pytest.fixture
def stat(g, trees):
    return TreeBasedStatistics(g, trees)


def test_count_and_proba(stat, trees):
    n_trees = len(trees)
    targets = list(range(1, 6))
    query = 0

    arr_c0 = np.array([0, 1, 1, 1, 2])
    arr_c1 = np.array([0, 1, 3, 1, 0])

    assert_eq_np(stat.count(query, condition=0, targets=targets),
                 arr_c0)
    assert_eq_np(stat.count(query, condition=1, targets=targets),
                 arr_c1)

    assert_eq_np(stat.proba(query, condition=0, targets=targets),
                 arr_c0 / 2)
    assert_eq_np(stat.proba(query, condition=1, targets=targets),
                 arr_c1 / 3)


def test_update_trees(stat, new_trees):
    stat.update_trees(new_trees, query=0, state=1)

    query = 1
    targets = [2, 3, 4, 5]
    arr_c0 = [1, 3, 2, 0]
    arr_c1 = [0, 0, 0, 0]

    assert_eq_np(stat.count(query, condition=0, targets=targets),
                 arr_c0)
    assert_eq_np(stat.count(query, condition=1, targets=targets),
                 arr_c1)


def test_update_trees_insufficient_trees(stat, new_trees):
    with pytest.raises(AssertionError):
        # insufficient length
        stat.update_trees(new_trees[:1], query=0, state=1)


@pytest.fixture
def trees1():
    return [
        {0, 1, 2},
        {1, 2},
        {1, 2, 3},
        {1, 2, 3, 4},
    ]


@pytest.fixture
def stat1(g, trees1):
    return TreeBasedStatistics(g, trees1)


def test_prediction_error(stat1):
    actual = stat1.prediction_error(0, 0, [3, 4])
    expected = entropy([1/3, 2/3]) * 2
    assert actual == expected


def test_query_score(stat1):
    actual = stat1.query_score(0, [3, 4])
    expected = entropy([1/3, 2/3]) * 2 * 3/4  # + error = 0 for state=1
    assert actual == expected
