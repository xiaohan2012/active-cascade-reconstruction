import argparse
from graph_helpers import load_graph_by_name, get_edge_weights


def normalize_globally(g):
    weights = get_edge_weights(g)
    deg = g.degree_property_map("out", weights)
    w_max = deg.a.max()
    print('old weight', weights.a)
    new_g = g.copy()
    new_weights = get_edge_weights(new_g)
    new_weights.a /= w_max
    new_deg = new_g.degree_property_map("out", new_weights)
    print('new weight (before self-loops)', new_weights.a)

    # add self-loops
    self_loops = [(v, v) for v in new_g.vertices()]
    new_g.add_edge_list(self_loops)

    # assign new weights
    new_weights = get_edge_weights(new_g)
    for v, v in self_loops:
        new_weights[new_g.edge(v, v)] = 1 - new_deg[v]
    print('new weight (after self-loops)', new_weights.a)

    new_g.edge_properties['weights'] = new_weights
    return new_g


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-g', '--graph', help='graph name')
    parser.add_argument('-s', '--graph_suffix', help='')
    parser.add_argument('-w', '--weighted', action='store_true', help='')
    parser.add_argument('-o', '--output_path', help='')
    
    args = parser.parse_args()
    
    g = load_graph_by_name(args.graph,
                           weighted=args.weighted,
                           suffix=args.graph_suffix)
    new_g = normalize_globally(g)

    new_g.save(args.output_path)
    print('saved to {}'.format(args.output_path))
    

if __name__ == '__main__':
    main()
