from tqdm import tqdm
from graph_helpers import observe_uninfected_node
from random_steiner_tree.util import isolate_vertex
from cascade_generator import gen_input
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

    def run(self,
            n_queries,
            obs=None,
            c=None,
            gen_input_kwargs={},
            iter_callback=None,
            force_receive_obs=False
    ):
        """return the list of query nodes
        """
        if obs is None or c is None:
            obs, c = gen_input(self.g, **gen_input_kwargs)[:2]

        if n_queries > 0 or force_receive_obs:
            self.q_gen.receive_observation(obs, c)

        aux = {'graph_changed': False,
               'obs': obs,
               'c': c}
        qs = []
        inf_nodes = list(obs)
        uninf_nodes = []
        
        if self.print_log:
            iters = tqdm(range(n_queries), total=n_queries)
        else:
            iters = range(n_queries)

        for i in iters:
            if self.print_log:
                print('iteration #{}'.format(i))

            try:
                q = self.q_gen.select_query(self.g, inf_nodes)
            except NoMoreQuery:
                if self.print_log:
                    print('no more nodes to query. queried {} nodes'.format(len(qs)))
                break

            # print('query:', q)
            qs.append(q)

            if len(qs) == n_queries:
                print('num. queries reached')
                break
            
            if c[q] == -1:  # not infected
                if self.print_log:
                    print('query {} is uninfected'.format(q))

                observe_uninfected_node(self.g, q, inf_nodes)
                if self.gi is not None:
                    isolate_vertex(self.gi, q)

                if self.print_log:
                    print('isolated node {}'.format(q))

                self.q_gen.update_pool(self.g)
                aux['graph_changed'] = True
                uninf_nodes.append(q)
            else:
                if self.print_log:
                    print('query {} is infected'.format(q))
                inf_nodes.append(q)

            # update tree samples if necessary
            if self.print_log:
                print('update samples started')
                pass

            label = int(c[q] >= 0)
            assert label in {0, 1}
            # print('update samples, node {} label {}'.format(q, label))
            try:
                self.q_gen.update_observation(self.g, inf_nodes, q, label, c)
            except NoMoreQuery:
                print('no more queries')
                break

            if self.print_log:
                print('update samples done')

            if callable(iter_callback):
                iter_callback(self.g, self.q_gen, inf_nodes, uninf_nodes)
            
        return qs, aux
