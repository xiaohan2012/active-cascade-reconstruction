
0. [X] generate the weighted graph
1. [X] generate IC cascade using random edge weight for different graphs
   - uniform random from `[0.001, 0.25]` (for grqc)
   - avg cascade size: 330 (for grqc)
2. [X] for query algorithms: entropy and prediction-error, make sure the sampling methods consider the edge weight
   - also run the sampling based algorithm on unweighted graph as baselines
3. inference algorithm consider the edge weight
   - weighted and unweighted version
