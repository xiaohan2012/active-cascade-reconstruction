import pytest
import numpy as np
from graph_tool import Graph
from graph_helpers import extract_nodes, extract_edges
from helpers import infected_nodes
from cascade_generator import ic, observe_cascade
from numpy.testing import assert_array_equal
from fixture import line, tree



@pytest.fixture
def p(line):
    p = line.new_edge_property('float')
    p.set_value(1.0)
    return p

@pytest.mark.parametrize("repeat", range(10))
@pytest.mark.parametrize("min_fraction", [0.25, 0.5, 0.75])
def test_ic_min_fraction(line, repeat, min_fraction):
    s, c, t = ic(line, 0.5, 0, max_fraction=1.0, min_fraction=min_fraction)
    assert len(infected_nodes(c)) >= (line.num_vertices() * min_fraction)
