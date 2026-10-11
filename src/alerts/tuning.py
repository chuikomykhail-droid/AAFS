"""Hyperparameters chosen once on the validation part (PLAN stage 6, D20), never on the test part.

Every candidate is fitted on the rows with t <= train_end - h (labels known when validation starts)
and scored by log loss on the validation rows. For LightGBM the number of trees comes from early
stopping on the same validation rows; the backtest then uses that fixed number.
"""
import itertools
import logging
import time

import pandas as pd

from alerts.config import ts
from alerts.metrics import score
from alerts.models.learned import GBMModel, LogisticModel

logger = logging.getLogger(__name__)


def tune(data: pd.DataFrame, h: int, cfg: dict) -> tuple[dict, pd.DataFrame]:
    ycol = f'y_{h}'
    lab = data[data[ycol].notna()]
    train = lab[lab['t'] <= ts(cfg['periods']['train_end']) - pd.Timedelta(hours=h)]
    val = lab[lab['part'] == 'val']
    y, yv = train[ycol].to_numpy(dtype=float), val[ycol].to_numpy(dtype=float)
    m = cfg['models']
    rows = []

    for C, hl in itertools.product(m['lr']['grid']['C'], m['lr']['grid']['half_life_days']):
        params = {'C': C, 'half_life_days': hl}
        t0 = time.time()
        p = LogisticModel(cfg, params).fit(train, y).predict_proba(val)
        rows.append({'model': 'LR', **params, **score(yv, p), 'seconds': time.time() - t0})

    g = m['lgbm']['grid']
    for nl, mcs, hl in itertools.product(g['num_leaves'], g['min_child_samples'], g['half_life_days']):
        params = {'num_leaves': nl, 'min_child_samples': mcs, 'half_life_days': hl,
                  'n_estimators': m['lgbm']['max_estimators']}
        t0 = time.time()
        model = GBMModel(cfg, params).fit(train, y, eval_set=(val, yv))
        params['n_estimators'] = int(model.model_.best_iteration_ or m['lgbm']['max_estimators'])
        rows.append({'model': 'LGBM', **params, **score(yv, model.predict_proba(val)), 'seconds': time.time() - t0})

    table = pd.DataFrame(rows)
    best = {}
    for name, keys in [('LR', ['C', 'half_life_days']),
                       ('LGBM', ['num_leaves', 'min_child_samples', 'half_life_days', 'n_estimators'])]:
        r = table[table['model'] == name].sort_values('log_loss').iloc[0]
        best[name] = {k: _value(k, r[k]) for k in keys}
        logger.info(f'h={h} tuned {name}: {best[name]} (val log loss {r["log_loss"]:.4f})')
    return best, table


def _value(key, v):
    if pd.isna(v):
        return None
    return float(v) if key == 'C' else int(v)
