import numpy as np
import pickle as pkl
from glob import glob
from scipy.spatial.distance import cdist


def load_cascades(dirname):
    for p in glob(dirname+'/*.pkl'):
        yield p, pkl.load(open(p, 'rb'))


def cascade_source(c):
    return np.nonzero((c == 0))[0][0]


def infected_nodes(c):
    return np.nonzero((c >= 0))[0]


def l1_dist(probas1, probas2):
    return cdist([probas1],
                 [probas2],
                 'minkowski', p=1.0)[0, 0]
