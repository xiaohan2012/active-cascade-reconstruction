# effects of cascade model and query using weights

using `grqc` as example: [figure](http://193.166.24.212/active-network-reconstruction/figs/average_precision_score/grqc-mic-o0.1.pdf)

Now, let's assume cascade are generated using edge probabilities

| query | weighted | unweighted |
|-------+----------+------------|
| IC    | [X]      | [X]        |
| SI    | []       | [X]        |


TODO: weighted/unweighted query on SI

conclusion:

- using weighted IC gives larger difference between `prediction_error` and `random` than SI model
- query using weighted or unweighted graph does not give much difference for both `prediction_error` and `entropy`
  - for `prediction_error`, the performance advantage is ~0.5% after 100 queries

# effects of weights on inferencing method

[figure](http://193.166.24.212/active-network-reconstruction/figs/average_precision_score/grqc-mic-o0.1-inference-with-weights-or-not.pdf)

conclusion:

using weights give better performance
