# sampling-steiner-tree

# main scripts

- `simulate_cascades.py`: simulate cascades and dump to files
- `generate_queries.py`: produce queries and dump to files
- `infer_from_queries.py`: infer the infection probabilities from queries

# todo

- [ ] efficient determinant computation on consecutive states
- [ ] random spanning tree sampling
- [ ] truncate the spanning tree to steiner tree
- [ ] metropolis-hasting algorithm for steiner tree sampling

# time

- `extract_steiner_tree`: `48.3%`
- `det_score_of_steiner_tree: `44.2%`