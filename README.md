# sampling-steiner-tree

# main python scripts

- `simulate_cascades.py`: simulate cascades and dump to files
- `generate_queries.py`: produce queries and dump to files
- `infer_from_queries.py`: infer the infection probabilities from queries
- `average_precision_score.ipynb`: evaluation using average precision score (should be better than precision and recall)

# shell shell scripts

- `scripts/query_{dataset}.sh`: generate queries for `${dataset}`
- `scripts/infer_{dataset}.sh`: make inference on infections for `${dataset}`