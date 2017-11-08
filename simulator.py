from graph_helpers import isolate_node, hide_disconnected_components
from experiment import gen_input


class Simulator():
    def __init__(self, g, query_generator):
        self.g = g
        self.q_gen = query_generator
        
    def run(self, n_queries):
        """return the list of query nodes
        """
        aux = {'graph_changed': False}
        obs, c = gen_input(self.g)

        qs = []
        inf_nodes = list(obs)
        for i in range(n_queries):
            q = self.q_gen.select_query(self.g, inf_nodes)
            qs.append(q)
            if c[q] == -1:  # not infected
                isolate_node(self.g, q)
                hide_disconnected_components(self.g, inf_nodes)
                self.q_gen.update_pool(self.g)
                aux['graph_changed'] = True
            else:
                inf_nodes.append(q)

        return qs, aux
