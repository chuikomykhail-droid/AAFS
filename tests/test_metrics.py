import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score

from alerts.metrics import bootstrap, score


def test_score_matches_sklearn_with_ties():
    rng = np.random.default_rng(0)
    for decimals in [1, 2, 6]:                      # coarse rounding gives many tied scores (baselines)
        y = (rng.random(4000) < 0.25).astype(float)
        p = np.round(0.2 + 0.3 * y * rng.random(4000) + 0.4 * rng.random(4000), decimals).clip(0.01, 0.99)
        s = score(y, p)
        assert abs(s['roc_auc'] - roc_auc_score(y, p)) < 1e-12
        assert abs(s['pr_auc'] - average_precision_score(y, p)) < 1e-12
        assert abs(s['brier'] - brier_score_loss(y, p)) < 1e-12
        assert abs(s['log_loss'] - log_loss(y, p)) < 1e-12


def test_bootstrap_is_paired_and_covers_the_point():
    rng = np.random.default_rng(1)
    n_days, per_day = 20, 200
    day = np.repeat(np.arange(n_days), per_day)
    y = (rng.random(n_days * per_day) < 0.3).astype(int)
    good = np.clip(0.3 + 0.4 * (y - 0.3) + 0.1 * rng.standard_normal(len(y)), 0.01, 0.99)
    preds = pd.DataFrame({'day': day, 'y': y, 'p_good': good, 'p_same': good, 'p_flat': 0.3})
    b = bootstrap(preds, ['good', 'same', 'flat'], 200, 0, reference='good').set_index(['model', 'metric'])
    for m in ['good', 'flat']:
        assert b.at[(m, 'brier'), 'lo'] <= b.at[(m, 'brier'), 'value'] <= b.at[(m, 'brier'), 'hi']
    assert b.at[('same', 'pr_auc'), 'diff_lo'] == b.at[('same', 'pr_auc'), 'diff_hi'] == 0   # identical model
    assert b.at[('flat', 'brier'), 'diff_lo'] > 0                                            # clearly worse
