from graph_tool.generation import lattice

from cascade_generator import si, observe_cascade
from query_selection import OurQueryGenerator
from inference import infer_infected_nodes
from eval_helpers import infection_precision_recall
from graph_helpers import (isolate_node, remove_filters,
                           hide_disconnected_components)


def gen_input(g, stop_fraction=0.25, p=0.1, q=0.1):
    s, c, _ = si(g, p, stop_fraction=stop_fraction)
    obs = observe_cascade(c, s, q)
    return obs, c

# @profile
def one_round_experiment(g, obs, c, q_gen, query_method,
                         n_queries=None,
                         debug=False):
    """
    str query_method: {'random', 'ours', 'pagerank}
    """
    if not debug:
        # if debug, we need to check how the graph is changed
        g = remove_filters(g)  # protect the original graph

    assert not g.is_directed()
    
    performance = []
    inf_nodes = list(obs)

    if n_queries is None:
        n_queries = len(q_gen.pool)
        
    for i in range(n_queries):
        if query_method in {'random', 'pagerank'}:
            q = q_gen.select_query()
        elif query_method == 'ours':
            q = q_gen.select_query(g, inf_nodes)
        else:
            raise ValueError('no such method..')

        if debug:
            print('query: {}'.format(q))

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
        preds = infer_infected_nodes(g, inf_nodes)

        scores = list(infection_precision_recall(preds, c, obs))
        performance.append(scores)
    return performance

if __name__ == '__main__':
    g = lattice((10, 10))
    obs, c = gen_input(g)
    our_gen = OurQueryGenerator(remove_filters(g), obs, num_spt=100, num_stt=5, use_resample=False)
    score = one_round_experiment(g, obs, c, our_gen, 'ours', 2)
    print(score)
