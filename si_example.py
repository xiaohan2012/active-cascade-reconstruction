import time
from graph_tool import load_graph
from tqdm import tqdm

from graph_helpers import get_edge_weights
from si import si_opt, si_naive


def main():
    g = load_graph('data/grqc/graph_weighted.gt')
    p = get_edge_weights(g)
    N = 100

    s = time.time()
    for i in tqdm(range(N), total=N):
        si_opt(g, p, source=None, stop_fraction=0.25)
    print("opt takes {} secs".format(time.time() - s))

    s = time.time()
    for i in tqdm(range(N), total=N):
        si_naive(g, p, source=None, stop_fraction=0.25)
    print("naive takes {} secs".format(time.time() - s))


if __name__ == '__main__':
    main()
