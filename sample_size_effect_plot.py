import pandas as pd
import pickle as pkl
import seaborn as sns
import matplotlib.pyplot as plt

from helpers import init_db

conn, cursor = init_db()

rows = []
cursor.execute("""
SELECT
    dataset, infer_n_samples, infer_sampling_method, metric_scores
FROM
    active.eval_per_cascade
WHERE
    metric_name = 'ap'
ORDER BY dataset, infer_n_samples, infer_sampling_method
""")

for r in cursor.fetchall():
    r = list(r)
    r[-1] = pkl.loads(r[-1])[0]
    rows.append(r)

df = pd.DataFrame(
    rows,
    columns=['dataset', 'n_samples', 'sampling_method', 'score']
)

agg_score = df.groupby(['dataset', 'n_samples', 'sampling_method']).mean()

agg_score.reset_index(inplace=True)  
g = sns.FacetGrid(agg_score, col="dataset",  hue="sampling_method")
g = (g.map(plt.semilogx, "n_samples", "score")
     .add_legend()
     .set_titles("{col_name}"))
g.savefig("/scratch/work/xiaoh1/data-active-cascade-reconstruction/outputs/figs/sample-size-effect/ap.pdf")
