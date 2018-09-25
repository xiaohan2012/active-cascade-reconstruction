import pytest
from numpy.testing import assert_array_equal

from si import si_opt
from fixture import g, line


@pytest.mark.parametrize(
    'g, stop_fraction, expected_time',
    [
        (line(), 1.0, [0, 1, 2, 3]),
        (line(), 0.5, [0, 1, -1, -1]),
    ])
def test_line(g, stop_fraction, expected_time):
    p = 1.0
    s, c, t = si_opt(
        g,
        p,
        source=0,
        stop_fraction=stop_fraction
    )

    assert s == 0
    assert_array_equal(c, expected_time)
