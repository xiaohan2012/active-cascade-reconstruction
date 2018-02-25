import numpy as np
import pickle as pkl
from tqdm import tqdm
from cascade_generator import si, ic, observe_cascade
from query_selection import EntropyQueryGenerator
from inference import infection_probability
from eval_helpers import top_k_infection_precision_recall
from graph_helpers import (isolate_node, remove_filters,
                           hide_disconnected_components,
                           load_graph_by_name)


def gen_input(g, source=None, cascade_path=None, stop_fraction=0.25, p=0.5, q=0.1, model='si', min_size=10):
    if cascade_path is None:
        if model == 'si':
            s, c, _ = si(g, p, stop_fraction=stop_fraction,
                         source=source)
        elif model == 'ic':
            while True:
                s, c, _ = ic(g, p, source=source)
                if np.sum(c >= 0) >= min_size:  # size is large enough
                    break
        else:
            raise ValueError('unknown cascade model')
    else:
        print('load from cache')
        c = pkl.load(open(cascade_path, 'rb'))
        s = np.nonzero([c == 0])[1][0]

    obs = observe_cascade(c, s, q)
    return obs, c

# @profile
def one_round_experiment(g, obs, c, q_gen, query_method, ks,
                         inference_method='sampling',
                         n_spanning_tree_samples=100,
                         subset_size=None,
                         n_queries=10,
                         return_details=False,
                         debug=False,
                         log=False):
    """
    str query_method: {'random', 'ours', 'pagerank}
    inference_method: {'min_steiner_tree', 'sampling'}
    ks: k values in top-`k` for evaluation

    return_details: bool, whether queries should be teturned

    Return:

    dict: k -> [(precision, recall), ...]
    """
    if not debug:
        # if debug, we need to check how the graph is changed
        g = remove_filters(g)  # protect the original graph

    assert not g.is_directed()
    
    performance = {k: [] for k in ks}  # grouped by k values
    inf_nodes = list(obs)

    queries = []
     
    if log:
        iters = tqdm(range(n_queries), total=n_queries)
    else:
        iters = range(n_queries)

    for i in iters:
        if query_method in {'random', 'pagerank'}:
            q = q_gen.select_query()
        elif query_method == 'ours':
            q = q_gen.select_query(g, inf_nodes)
        else:
            raise ValueError('no such method..')

        if debug:
            print('query: {}'.format(q))

        queries.append(q)

        if c[q] == -1:
            # uninfected
            # remove it from graph
            # ignore for now
            # filter the node will change the vertex index
            isolate_node(g, q)
            hide_disconnected_components(g, inf_nodes)
            q_gen.update_pool(g)
        else:
            inf_nodes.append(q)

        if inference_method == 'sampling':
            probas = infection_probability(g, inf_nodes,
                                           n_samples=n_spanning_tree_samples,
                                           subset_size=subset_size)
        else:
            print('try {} later'.format(inference_method))

        for k in ks:
            scores = top_k_infection_precision_recall(
                g, probas, c, obs, k)
            performance[k].append(scores)

    if return_details:
        return performance, queries
    else:
        return performance

if __name__ == '__main__':
    g = load_graph_by_name('karate')
    obs, c = gen_input(g)
    our_gen = EntropyQueryGenerator(remove_filters(g), obs, num_spt=100, num_stt=5, use_resample=True)
    score = one_round_experiment(g, obs, c, our_gen, 'ours', 10, log=True)
    print(score)
