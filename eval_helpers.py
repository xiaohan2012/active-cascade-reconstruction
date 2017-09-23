def infection_precision_recall(preds, c, obs, return_details=False):
    """
    given set of inferred infected nodes and ground truth, return precision and recall

    Args:
    set of ints: preds, set of predicted infections (besides observations)
    np.ndarray:  c, cascade
    bool: return_details, if the corret, false_positive, false_negative should be returned

    Return:
    float: precison
    float: recall
    dict: detail of correct, fp, np keyed by the name
    """
    all_infs = set((c >= 0).nonzero()[0])
    # print('all_infs:', all_infs)
    remain_infs = all_infs - set(obs)
    correct = preds.intersection(remain_infs)
    preds -= set(obs)
    # print('correct: ', correct)
    # print("preds: ", preds)
    # print('remain_infs: ', remain_infs)
    precision = len(correct) / len(preds)
    recall = len(correct) / len(remain_infs)

    if not return_details:
        return precision, recall
    else:
        detail = {'correct': correct,
                  'fp': preds - correct,  # is not infected but classified as infected
                  'fn': remain_infs - preds,  # is infected but classified as not infected
                  'prec': precision,
                  'rec': recall}
        
        return precision, recall, detail
