# coding: utf-8

import pickle as pkl
import os
import numpy as np
from graph_tool.draw import sfdp_layout
from matplotlib import pyplot as plt

from helpers import (
    infected_nodes,
    cascade_source,
    makedir_if_not_there
)
from graph_helpers import load_graph_by_name
from viz_helpers import (
    lattice_node_pos,
    query_plot_setting,
    visualize,
    default_plot_setting,
    QueryProcessIllustrator,
    set_cycler
)
from eval_helpers import get_scores_by_queries


plt.switch_backend('cairo')

graph_name = 'lattice-100'
g = load_graph_by_name(graph_name, suffix='_weighted_0.5')

if graph_name == 'lattice-100':
    pos = lattice_node_pos(g, shape=(10, 10))
else:
    pos = sfdp_layout(g)


round_id = 11
cascade_size = 0.25
obs_fraction = 0.25
cascade_model = 'si'
sampling_method = 'simulation'

n_queries_to_show = 10

data_id = '{graph_name}-m{cascade_model}-s{cascade_size}-o{obs_fraction}-omuniform'.format(
    graph_name=graph_name,
    cascade_model=cascade_model,
    cascade_size=cascade_size,
    obs_fraction=obs_fraction
)


query_methods = ['random', 'pagerank', 'entropy', 'cond-entropy']
(obs, c) = pkl.load(
    open('cascade-weighted/{data_id}/{round_id}.pkl'.format(
        data_id=data_id,
        round_id=round_id),
         'rb')
)

# ----------------
# plot the queries in one plot (for each query method)
# ----------------

queries_by_method = {}
for query_method in query_methods:
    queries_by_method[query_method] = pkl.load(
        open('outputs/queries-weighted/{data_id}/{sampling_method}/{query_method}/{round_id}.pkl'.format(
            data_id=data_id,
            sampling_method=sampling_method,
            query_method=query_method,
            round_id=round_id),
             'rb'))[0]
n_queries = len(queries_by_method['random'])

fig_dir = os.path.join(
    'figs/query-process-illustration',
    data_id, str(round_id)
)
makedir_if_not_there(fig_dir)

setting = default_plot_setting(g, c, obs, size_multiplier=1.5)
visualize(g, pos, **setting, output=os.path.join(fig_dir, 'cascade.pdf'))


for name in queries_by_method:
    queries = queries_by_method[name][:n_queries_to_show]

    setting = query_plot_setting(
        g, c, obs, queries,
        node_size=36,
        indicator_type='color'
    )
    visualize(
        g,
        pos,
        **setting,
        output=os.path.join(fig_dir, '{}.pdf'.format(name))
    )


# ------------------------------------
# plot the score
# vs. different query iterations
# ------------------------------------

eval_method = 'ap'
every = 5
n_queries_to_show = 30

plt.style.use('paper')

query_dir = 'outputs/queries-weighted/{}/{}/'.format(data_id, sampling_method)
probas_dir = 'outputs/inf-probas-weighted/{}/{}/'.format(data_id, sampling_method)


def load_qs_and_probas(query_method):
    query_file_path = os.path.join(query_dir, query_method, '{}.pkl'.format(round_id))
    proba_file_path = os.path.join(probas_dir, query_method, '{}.pkl'.format(round_id))
    
    qs, _ = pkl.load(open(query_file_path, 'rb'))
    probas = pkl.load(open(proba_file_path, 'rb'))
    qs = qs[:n_queries_to_show]
    n_probas_to_show = int(n_queries_to_show / every)
    probas = probas[:n_probas_to_show+1]
    return qs, probas

inf_nodes = infected_nodes(c)
source = cascade_source(c)


eval_methods = dict(
    ap=dict(eval_with_mask=True),
    l1=dict(eval_with_mask=True)
)
for eval_method, kwargs in eval_methods.items():
    fig, ax = plt.subplots(1, 1)
    set_cycler(ax)
    
    for query_method in query_methods:
        qs, probas = load_qs_and_probas(query_method)
        scores = get_scores_by_queries(
            qs, probas, c, obs, eval_method=eval_method,
            every=every,
            eval_with_mask=True,
        )

        x = np.arange(0, len(scores)) * every
        x += 1  # #queries starts from 1
        ax.plot(x, scores)

    ax.legend(query_methods, loc='best', fontsize=16)
    ax.set_title(eval_method)

    output_path = '{}/{}_score.pdf'.format(fig_dir, eval_method)
    fig.savefig(output_path)
    print('{} saved to {}'.format(eval_method, output_path))

# ---------------------
# illustrate the query process by plotting queries at different snapshots
# ---------------------

for query_method in query_methods:
    illus = QueryProcessIllustrator(
        g, obs, c, pos
    )
    qs, probas = load_qs_and_probas(query_method)
    n_col = len(probas) - 1
    size = 7.5
    fig, axes = plt.subplots(1, n_col, figsize=(n_col * size, size))
    for ax in axes:
        ax.axis('off')
    for i, q in enumerate(qs):
        illus.add_query(q)
        if i % every == 0:
            proba_index = int(i / every)
            ax = axes[proba_index]
            illus.plot_snapshot(q, probas[proba_index], ax=ax)
            title = "|Q|={n_queries}, |H|={n_hidden_infs}".format(
                n_queries=i,
                n_hidden_infs=len(illus.hidden_inf)+1
            )
            ax.set_title(title)
    output_path = '{}/{}_query_process.pdf'.format(fig_dir, query_method)
    print('query process saved to {}'.format(output_path))
    fig.savefig(output_path)

