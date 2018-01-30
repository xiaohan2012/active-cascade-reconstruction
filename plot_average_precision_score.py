# coding: utf-8

import numpy as np
import matplotlib
import argparse
matplotlib.use('pdf')

from matplotlib import pyplot as plt
    
from helpers import load_cascades
from graph_helpers import load_graph_by_name
from eval_helpers import aggregate_scores_over_cascades_by_methods

np.seterr(divide='raise', invalid='raise')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-g', '--graph_name', help='graph name')
    parser.add_argument('-c', '--cascade_pattern', help='cascade pattern')
    parser.add_argument('-n', '--n_queries', type=int, help='number of queries to show')
    parser.add_argument('-s', '--sampling_method', help='')
    parser.add_argument('-i', '--inf_method', help='')
    parser.add_argument('-q', '--query_methods', required=True,
                        help='list of query methods separated by ","')
    parser.add_argument('-l', '--legend_labels',
                        help='list of labels to show in legend separated  by ","')
    parser.add_argument('-f', '--fig_name', help='figure name')

    args = parser.parse_args()

    inf_result_dirname = 'outputs/{}/{}/{}'.format(args.inf_method,
                                                   args.cascade_pattern, args.sampling_method)
    query_dirname = 'outputs/queries/{}/{}'.format(args.cascade_pattern, args.sampling_method)

    # if n_queries is too large, e.g, 100,
    # we might have no hidden infected nodes left and average precision score is undefined
    n_queries = args.n_queries

    g = load_graph_by_name(args.graph_name)

    methods = list(map(lambda s: s.strip(), args.query_methods.split(',')))
    if args.legend_labels is not None:
        labels = list(map(lambda s: s.strip(), args.legend_labels.split(',')))
    else:
        labels = methods
    print('query_methods:', methods)
    print('labels:', labels)
    
    cascades = load_cascades('cascade/' + args.cascade_pattern)

    scores_by_method = aggregate_scores_over_cascades_by_methods(
        cascades, methods,
        n_queries,
        inf_result_dirname,
        query_dirname)

    plt.clf()

    fig, ax = plt.subplots(figsize=(5, 4))
    
    for method in methods:
        scores = np.array(scores_by_method[method], dtype=np.float32)
        mean_scores = np.mean(scores, axis=0)
        # print(np.std(scores,axis=0))
        ax.plot(mean_scores)
        # ax.hold(True)
    ax.legend(labels, loc='best')
    fig.tight_layout()

    ax.xaxis.label.set_fontsize(20)
    ax.yaxis.label.set_fontsize(20)

    # plt.ylim(0.2, 0.8)
    fig.savefig('figs/average_precision_score/{}.pdf'.format(args.fig_name))

