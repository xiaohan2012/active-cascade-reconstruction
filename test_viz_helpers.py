import matplotlib as mpl
mpl.use('Agg')

import numpy as np
from viz_helpers import QueryIllustrator as qi
from fixture import g, obs


def test_query_illustrator(g, obs):        
    c =  qi.node_colors(g, obs, 
                        [11], {2}, {3}, {4})
    
    assert set(c.a) == set(range(6))
    for o in obs:
        c.a[o] = qi.OBS
    c.a[11] = qi.QUERY
    c.a[2] = qi.CORRECT
    c.a[3] = qi.FP
    c.a[4] = qi.FN
