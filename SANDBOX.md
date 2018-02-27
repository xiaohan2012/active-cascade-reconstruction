
0. [X] generate the weighted graph
1. [X] generate IC cascade using random edge weight for different graphs
   - uniform random from `[0.001, 0.25]` (for grqc)
   - avg cascade size: 330 (for grqc)
2. [X] for query algorithms: entropy and prediction-error, make sure the sampling methods consider the edge weight
   - also run the sampling based algorithm on unweighted graph as baselines
3. inference algorithm consider the edge weight
   - weighted and unweighted version

# effects of cascade model

[figure](http://193.166.24.212/active-network-reconstruction/figs/average_precision_score/grqc-mic-o0.1.pdf)

conclusion:

- using weighted IC gives larger difference between `prediction_error` and `random` than SI model
- query using weighted or unweighted graph does not give much difference for both `prediction_error` and `entropy`

# effects of weights on inferencing method

TBD