import pandas as pd
import numpy as np
import pickle as pkl
import re
import seaborn as sns
import matplotlib.pyplot as plt

from helpers import init_db

conn, cursor = init_db()

metric = 'ap'
n_queries = 30
rows = []
cursor.execute("""
SELECT
    dataset, query_method, metric_scores
FROM
    active.eval_per_cascade
WHERE
    metric_name = '{metric}'
    AND n_queries = {n_queries}
    AND query_sampling_method = 'naive'
    AND infer_sampling_method = 'naive'
ORDER BY dataset, query_method
""".format(metric=metric, n_queries=n_queries)
)

for r in cursor.fetchall():
    r = list(r)
    r[-1] = pkl.loads(r[-1])
    rows.append(r)

df = pd.DataFrame(
    rows,
    columns=['dataset', 'query_method', metric]
)

df['cascade_model'] = df['dataset'].apply(lambda s: re.findall('-m([\w]+)-', s)[0].upper())
df['graph'] = df['dataset'].apply(lambda s: re.findall('([\-a-z0-9]+)-m', s)[0])

exploded_rows = []
for name, grouped in df.groupby(['graph', 'cascade_model', 'query_method'])[metric]:
    avg_scores = np.array(grouped.tolist()).mean(axis=0)
    for i, score in enumerate(avg_scores):
        exploded_rows.append(name + (i, score))

agg_score = pd.DataFrame(
    exploded_rows,
    columns=['graph', 'cascade_model', 'query_strategy', 'num_queries', metric.upper()]
)

# agg_score.reset_index(inplace=True)

g = sns.FacetGrid(
    agg_score,
    row='cascade_model',
    col="graph",
    hue="query_strategy"
)
g = (g.map(plt.plot, "num_queries", metric.upper())
     .add_legend()
     .set_titles("{col_name}, {row_name}"))
g.savefig(
    "/scratch/work/xiaoh1/data-active-cascade-reconstruction/outputs/figs/query_strategy/{metric}.pdf".format(
        metric=metric
    )
)




