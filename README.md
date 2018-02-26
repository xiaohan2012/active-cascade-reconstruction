# sampling-steiner-tree

# main python scripts

- `make_graph_weighted.py`: dump  graph with edge weights
- `simulate_cascades.py`: simulate cascades and dump to files
- `generate_queries.py`: produce queries and dump to files
- `infer_from_queries.py`: infer the infection probabilities from queries
- `average_precision_score.ipynb`: evaluation using average precision score (should be better than precision and recall)


# shell scripts

## cascade generation

- `gen_cascades_with_varying_size.sh`
- `gen_cascades_with_varying_obs_fraction.sh`

## query

- `query_cascades_with_varying_size.sh`
- `query_cascades_with_varying_obs_fraction.sh`
- `query_weighted_graph.sh`: on weighted graph

## inference

- `infer_weighted_cascade.sh`: on weighted graph
- `infer_cascades_with_varying_size.sh`: TBD
- `infer_cascades_with_varying_obs_fraction.sh`: TBD


# misc

- `scripts/query_{dataset}.sh`: generate queries for `${dataset}`
- `scripts/infer_{dataset}.sh`: make inference on infections for `${dataset}`
- `compare_running_time.py`: script to compare running time for different query methods
- `print_cascade_sizes.py`: print simulated cascade statistics

