import pytest
import numpy as np
from graph_helpers import load_graph_by_name
from experiment import gen_input
from itertools import combinations

@pytest.fixture
def g():
    return load_graph_by_name('grqc', weighted=True)


# try random roots on IC model
@pytest.mark.parametrize("source", [np.random.choice(1000) for i in range(10)])
def test_gen_input_ic_model(g, source):
    p = g.edge_properties['weights'].a
    
    rows = [gen_input(g, p=p, model='ic', source=source)
            for i in range(10)]

    # make sure each is different from other sampled cascades
    for r1, r2 in combinations(rows, 2):
        obs1, c1 = r1
        obs2, c2 = r2
        assert set(obs1) != set(obs2)
    
        
