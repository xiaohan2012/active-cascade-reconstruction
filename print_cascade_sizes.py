import pickle as pkl
from glob import glob

os = [pkl.load(open(p, 'rb'))[0] for p in glob('cascade-weighted/grqc-mic-o0.1/*')]
sizes = [len(o) for o in os]
