import numpy as np
from linalg_helpers import num_spanning_trees_dense
from graph_helpers import contract_graph_by_nodes, extract_nodes


def det_score_of_steiner_tree(st, g):
    """
    Param:
    --------
    st: GraphView, steiner tree
    
    Returns:
    --------
    returns its score of being sampled by the truncate algorithm
    
    the score is computed as the determinant of the contracted graph of g on st.vertices()
    """
    cg, weights = contract_graph_by_nodes(g, extract_nodes(st))
    return num_spanning_trees_dense(cg, weights)


def resample(steiner_trees, g, m):
    """resample the trees with probability proportional to their real score / determinant score
    m: number of sub-samples to draw
    """
    det_scores = [det_score_of_steiner_tree(st, g)
                  for st in steiner_trees]
    real_scores = np.exp([-st.num_edges() for st in steiner_trees])
    sampling_importance = real_scores / np.array(det_scores)
    sampling_importance /= sampling_importance.sum()

    resampled_ids = np.random.choice(np.arange(len(steiner_trees)), m, replace=False, p=sampling_importance)
    return [steiner_trees[i] for i in resampled_ids]
