import numpy as np
import pickle as pkl
from glob import glob


def load_cascades(dirname):
    for p in glob(dirname+'/*.pkl'):
        yield p, pkl.load(open(p, 'rb'))


def cascade_source(c):
    return np.nonzero((c == 0))[0][0]
