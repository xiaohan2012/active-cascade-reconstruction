from graph_tool import GraphView
from graph_tool.generation import lattice

from cascade_generator import si, observe_cascade
from query_selection import RandomQueryGenerator, OurQueryGenerator
from inference import infer_infected_nodes
from eval_helpers import infection_precision_recall
from graph_helpers import isolate_node


def gen_input(g, p=0.1, q=0.1):
    s, c, _ = si(g, p)
    obs = observe_cascade(c, s, q)
    return obs, c


def one_round_experiment(g, obs, c, q_gen, query_method, n_queries=None):
    """
    str query_method: {'random', 'ours'}
    """    
    efilt = g.new_edge_property('bool')
    efilt.set_value(True)
    g = GraphView(g, efilt=efilt)
    
    performance = []
    inf_nodes = list(obs)

    if n_queries is None:
        n_queries = len(q_gen.pool)
        
    for i in range(n_queries):
        if query_method == 'random':
            q = q_gen.select_query()
        elif query_method == 'ours':
            q = q_gen.select_query(g, inf_nodes)
        else:
            raise ValueError('no such method..')

        if c[q] == -1:
            # uninfected
            # remove it from graph
            # ignore for now
            # filter the node will change the vertex index
            isolate_node(g, q)
        else:
            inf_nodes.append(q)
        preds = infer_infected_nodes(g, inf_nodes)

        scores = list(infection_precision_recall(preds, c, obs))
        performance.append(scores)
    return performance

if __name__ == '__main__':
    g = lattice((10, 10))
    obs, c = gen_input(g)
    score = one_round_experiment(g, obs, c)
    print(score)
