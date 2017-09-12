def infection_precision_recall(preds, c, obs):    
    """
    given set of inferred infected nodes and ground truth, return precision and recall

    Args:
    set of ints: preds, set of predicted infections (besides observations)
    np.ndarray:  c, cascade
    
    Return:
    float: precison
    float: recall
    """
    all_infs = set((c >= 0).nonzero()[0])
    remain_infs = all_infs - set(obs)
    correct = preds.intersection(remain_infs)
    precision = len(correct) / len(preds)
    recall = len(correct) / len(remain_infs)
    return precision, recall
