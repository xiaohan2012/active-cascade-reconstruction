import argparse
import numpy as np
from graph_helpers import load_graph_by_name


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-g', '--graph', help='graph name')
    parser.add_argument('--p_min', default=0.0, type=float,
                        help='lower bound for edge weight')
    parser.add_argument('--p_max', default=1.0, type=float,
                        help='upper bound for edge weight')
    args = parser.parse_args()
    g = load_graph_by_name(args.graph)

    weights = g.new_edge_property('float')
    weights.a = np.random.random(g.num_edges()) * (args.p_max - args.p_min) + args.p_min

    g.edge_properties["weights"] = weights

    output_path = 'data/{}/graph_weighted.gt'.format(args.graph)
    g.save(output_path)
    
    print('dumped to {}'.format(output_path))

if __name__ == '__main__':
    main()
