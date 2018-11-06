import pytest
from numpy.testing import assert_array_equal

from si import si_opt
from exceptions import TooManyInfections
from fixture import g, line


@pytest.mark.parametrize(
    'g, max_fraction, expected_time',
    [
        (line(), 1.0, [0, 1, 2, 3]),
        (line(), 0.5, [0, 1, -1, -1]),
    ])
def test_line(g, max_fraction, expected_time):
    p = 1.0
    s, c, t = si_opt(
        g,
        p,
        source=0,
        max_fraction=max_fraction
    )

    assert s == 0
    assert_array_equal(c, expected_time)


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
    s, c, t = si_opt(
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
        si_opt(line, 1.0, infected=[0, 1, 2], max_fraction=0.5)
