import pandas as pd
import pickle as pkl
import re
import seaborn as sns
import matplotlib.pyplot as plt

from helpers import init_db

conn, cursor = init_db()

metric = 'ap'

rows = []
cursor.execute("""
SELECT
    dataset, infer_n_samples, infer_sampling_method, metric_scores
FROM
    active.eval_per_cascade
WHERE
    metric_name = '{metric}'
    AND infer_n_samples <= 2560
ORDER BY dataset, infer_n_samples, infer_sampling_method
""".format(metric=metric)
)

for r in cursor.fetchall():
    r = list(r)
    r[-1] = pkl.loads(r[-1])[0]
    rows.append(r)

df = pd.DataFrame(
    rows,
    columns=['dataset', 'n_samples', 'sampling_method', metric]
)
df['cascade_model'] = df['dataset'].apply(lambda s: re.findall('-m([\w]+)-', s)[0].upper())
df['graph'] = df['dataset'].apply(lambda s: re.findall('([\-a-z0-9]+)-m', s)[0])

agg_score = df.groupby(['graph', 'cascade_model', 'sampling_method', 'n_samples']).mean()

agg_score.reset_index(inplace=True)

g = sns.FacetGrid(
    agg_score,
    row='cascade_model',
    col="graph",
    hue="sampling_method"
)
g = (g.map(plt.semilogx, "n_samples", metric)
     .add_legend()
     .set_titles("{col_name}, {row_name}"))
g.savefig(
    "/scratch/work/xiaoh1/data-active-cascade-reconstruction/outputs/figs/sample-size-effect/{metric}.pdf".format(
        metric=metric
    )
)
