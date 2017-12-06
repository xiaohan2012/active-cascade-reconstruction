from tqdm import tqdm
from graph_helpers import isolate_node, hide_disconnected_components
from experiment import gen_input


class Simulator():
    def __init__(self, g, query_generator, print_log=False):
        self.g = g
        self.q_gen = query_generator
        self.print_log = print_log

    def run(self, n_queries, obs=None, c=None):
        """return the list of query nodes
        """
        if obs is None or c is None:
            obs, c = gen_input(self.g)

        self.q_gen.receive_observation(obs)

        aux = {'graph_changed': False,
               'obs': obs,
               'c': c}
        qs = []
        inf_nodes = list(obs)

        if self.print_log:
            iters = tqdm(range(n_queries), total=n_queries)
        else:
            iters = range(n_queries)

        for i in iters:
            q = self.q_gen.select_query(self.g, inf_nodes)
            # print('query:', q)
            qs.append(q)
            
            if c[q] == -1:  # not infected
                isolate_node(self.g, q)
                hide_disconnected_components(self.g, inf_nodes)
                self.q_gen.update_pool(self.g)
                aux['graph_changed'] = True
            else:
                inf_nodes.append(q)

            # update tree samples if necessary
            if hasattr(self.q_gen, 'update_samples'):
                # print('update samples')
                label = int(c[q] >= 0)
                assert label in {0, 1}
                self.q_gen.update_samples(self.g, inf_nodes, q, label)
                
        return qs, aux
