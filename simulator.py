from tqdm import tqdm
from graph_helpers import observe_uninfected_node
from random_steiner_tree.util import isolate_vertex
from experiment import gen_input
from query_selection import NoMoreQuery


class Simulator():
    def __init__(self, g, query_generator, gi=None, print_log=False):
        """
        g: graph_tool.Graph or graph_tool.GraphView
        gi: random_steiner_tree.Graph
        """
        self.g = g
        self.gi = gi
        self.q_gen = query_generator
        self.print_log = print_log

    # @profile
    def run(self, n_queries, obs=None, c=None):
        """return the list of query nodes
        """
        if obs is None or c is None:
            obs, c = gen_input(self.g)

        self.q_gen.receive_observation(obs, c)

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
            try:
                q = self.q_gen.select_query(self.g, inf_nodes)
            except NoMoreQuery:
                if self.print_log:
                    print('no more nodes to query. queried {} nodes'.format(len(qs)))
                break

            # print('query:', q)
            qs.append(q)
            
            if c[q] == -1:  # not infected
                if self.print_log:
                    # print('isolating node {} started'.format(q))
                    pass

                observe_uninfected_node(self.g, q, inf_nodes)
                if self.gi is not None:
                    isolate_vertex(self.gi, q)

                if self.print_log:
                    # print('isolating node {} done'.format(q))
                    pass

                self.q_gen.update_pool(self.g)
                aux['graph_changed'] = True
            else:
                inf_nodes.append(q)

            # update tree samples if necessary
            if hasattr(self.q_gen, 'update_samples'):
                if self.print_log:
                    print('update samples started')
                    pass

                label = int(c[q] >= 0)
                assert label in {0, 1}
                self.q_gen.update_samples(self.g, inf_nodes, q, label, c)

                if self.print_log:
                    print('update samples done')
                
        return qs, aux
