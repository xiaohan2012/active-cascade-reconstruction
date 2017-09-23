import numpy as np
from eval_helpers import infection_precision_recall


def test_infection_precision_recall():
    preds = {0, 1, 2}
    c = np.array([-1, 0, 1, 2, -1])
    obs = [1]
    prec, rec, detail = infection_precision_recall(
        preds, c, obs, return_details=True)
    assert prec == 0.5
    assert rec == 0.5
    assert detail['correct'] == {2}
    assert detail['fp'] == {0}
    assert detail['fn'] == {3}
