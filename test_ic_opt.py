import pytest
from numpy.testing import assert_array_equal, assert_almost_equal

from ic import ic_opt
from fixture import g, line
from helpers import infected_nodes
from exceptions import TooManyInfections

from collections import Counter
from tqdm import tqdm


@pytest.mark.parametrize(
    'g, max_fraction, expected_time',
    [
        (line(), 1.0, [0, 1, 2, 3]),
        (line(), 0.5, [0, 1, -1, -1]),
    ])
def test_line(g, max_fraction, expected_time):
    p = 1.0
    s, c, t = ic_opt(
        g,
        p,
        source=0,
        max_fraction=max_fraction
    )

    assert s == 0
    assert_array_equal(c, expected_time)


def test_zero_point_five_case(line):
    p = 0.5
    occ = []
    N = int(1e3)
    for i in tqdm(range(N), total=N):
        s, c, t = ic_opt(
            line,
            p,
            source=0,
            max_fraction=1.0
        )

        n_infected = len(infected_nodes(c))
        occ.append(n_infected)
    freq = Counter(occ)
    probas = {i: freq[i] / N for i in range(1, 5)}

    assert_almost_equal(probas[1], 0.5, decimal=1)
    assert_almost_equal(probas[2], 0.25, decimal=1)
    assert_almost_equal(probas[3], 0.125, decimal=1)
    assert_almost_equal(probas[4], 0.125, decimal=1)


@pytest.mark.parametrize(
    'g, infected, max_fraction, expected_time',
    [
        (line(), [0, 3], 1.0, [0, 1, 1, 0]),
        (line(), [0, 1], 1.0, [0, 0, 1, 2]),
        (line(), [0, 1, 2, 3], 1.0, [0, 0, 0, 0]),
        (line(), [0, 3], 0.5, [0, -1, -1, 0]),
    ])
def test_input_with_infected(g, infected, max_fraction, expected_time):
    g.set_directed(False)  # to undirected
    p = 1.0
    s, c, t = ic_opt(
        g,
        p,
        source=None,
        max_fraction=max_fraction,
        infected=infected,
        verbose=5
    )

    assert s is None
    assert_array_equal(c, expected_time)


def test_input_with_too_many_infected(line):
    with pytest.raises(TooManyInfections):
        ic_opt(line, 1.0, infected=[0, 1, 2], max_fraction=0.5)
