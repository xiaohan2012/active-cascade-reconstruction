import pickle as pkl
from glob import glob


def load_cascades(dirname):
    for p in glob(dirname+'/*.pkl'):
        yield p, pkl.load(open(p, 'rb'))
