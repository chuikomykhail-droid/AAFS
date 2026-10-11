"""Metrics, day-block bootstrap and calibration (PLAN stage 4, D18).

Units are strongly correlated within a moment (waves), so rows are not independent: the bootstrap
resamples whole forecast days with replacement. The same day draws are used for every model,
which gives paired confidence intervals for differences between models.

PR-AUC and ROC-AUC are computed here with one sort per call and exact handling of tied scores
(baselines produce many ties); tests check them against scikit-learn.
"""
import numpy as np
import pandas as pd

EPS = 1e-6
METRICS = ['pr_auc', 'roc_auc', 'brier', 'log_loss']
HIGHER_IS_BETTER = {'pr_auc': True, 'roc_auc': True, 'brier': False, 'log_loss': False}


def score(y: np.ndarray, p: np.ndarray) -> dict:
    y = np.asarray(y, dtype=float)
    p = np.clip(np.asarray(p, dtype=float), EPS, 1 - EPS)
    out = {'brier': float(np.mean((p - y) ** 2)),
           'log_loss': float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))}
    n_pos = y.sum()
    n_neg = len(y) - n_pos
    if n_pos == 0 or n_neg == 0:
        return {'pr_auc': np.nan, 'roc_auc': np.nan, **out}
    values, inverse, counts = np.unique(p, return_inverse=True, return_counts=True)   # ascending
    pos = np.bincount(inverse, weights=y, minlength=len(values))
    # ROC-AUC from average ranks (Mann-Whitney U)
    avg_rank = np.cumsum(counts) - (counts - 1) / 2
    out['roc_auc'] = float(((avg_rank * pos).sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))
    # PR-AUC as average precision over distinct thresholds, highest score first
    tp = np.cumsum(pos[::-1])
    seen = np.cumsum(counts[::-1])
    recall_step = pos[::-1] / n_pos
    out['pr_auc'] = float((recall_step * tp / seen).sum())
    return {k: out[k] for k in METRICS}


def bootstrap(preds: pd.DataFrame, models: list, n_reps: int, seed: int, ci: float = 0.95,
              reference: str | None = None) -> pd.DataFrame:
    """Point estimate and percentile CI per model and metric, resampling forecast days.

    With `reference`, also the paired difference (model - reference) and its CI.
    """
    day = preds['day'].to_numpy()
    uniq = np.unique(day)
    by_day = [np.flatnonzero(day == d) for d in uniq]
    y = preds['y'].to_numpy(dtype=float)
    P = {m: preds[f'p_{m}'].to_numpy() for m in models}
    rng = np.random.default_rng(seed)
    draws = {m: {k: np.empty(n_reps) for k in METRICS} for m in models}
    for r in range(n_reps):
        idx = np.concatenate([by_day[i] for i in rng.integers(0, len(uniq), len(uniq))])
        for m in models:
            s = score(y[idx], P[m][idx])
            for k in METRICS:
                draws[m][k][r] = s[k]

    a = (1 - ci) / 2
    rows = []
    for m in models:
        point = score(y, P[m])
        for k in METRICS:
            row = {'model': m, 'metric': k, 'value': point[k],
                   'lo': _quantile(draws[m][k], a), 'hi': _quantile(draws[m][k], 1 - a)}
            if reference is not None:
                diff = draws[m][k] - draws[reference][k]
                row.update(diff=point[k] - score(y, P[reference])[k],
                           diff_lo=_quantile(diff, a), diff_hi=_quantile(diff, 1 - a))
            rows.append(row)
    out = pd.DataFrame(rows)
    out.attrs.update(n_rows=len(y), n_pos=int(y.sum()), n_days=len(uniq))
    return out


def _quantile(x: np.ndarray, q: float) -> float:
    """Quantile over defined draws; NaN when the metric is undefined in every draw (no positives)."""
    x = x[~np.isnan(x)]
    return float(np.quantile(x, q)) if len(x) else np.nan


def calibration(y: np.ndarray, p: np.ndarray, n_bins: int = 10) -> pd.DataFrame:
    """Reliability table: quantile bins of the prediction, mean prediction vs observed rate."""
    d = pd.DataFrame({'y': y, 'p': p})
    d['bin'] = pd.qcut(d['p'].rank(method='first'), n_bins, labels=False)
    return d.groupby('bin').agg(p_mean=('p', 'mean'), y_rate=('y', 'mean'), n=('y', 'size')).reset_index(drop=True)
