"""Walk-forward backtest with daily retraining (PLAN stage 4, D18).

For every forecast day D (UTC midnight to midnight) a fresh model is fitted on the rows with
t <= D - h, whose labels (t, t+h] are fully known by D, and predicts the rows with t in [D, D + 1 day).
Rows without a label for this horizon (D17) are never used.
"""
import logging
import time

import numpy as np
import pandas as pd

from alerts.config import ts

logger = logging.getLogger(__name__)
DAY = pd.Timedelta(days=1)


def days(cfg: dict, part: str) -> pd.DatetimeIndex:
    """Forecast days of the validation or test part."""
    p = cfg['periods']
    lo, hi = {'val': (p['train_end'], p['val_end']), 'test': (p['val_end'], cfg['data_end'])}[part]
    return pd.date_range(ts(lo), ts(hi), freq='D', inclusive='left')


def walk_forward(data: pd.DataFrame, h: int, forecast_days, make_model) -> pd.DataFrame:
    """Predictions for every labelled row of the forecast days: columns row (index of data), day, p.

    make_model() returns a fresh unfitted model with fit(X, y) / predict_proba(X).
    """
    ycol = f'y_{h}'
    lab = data[data[ycol].notna()]
    t = lab['t']
    y = lab[ycol].to_numpy(dtype=float)
    out = []
    for day in forecast_days:
        train = (t <= day - pd.Timedelta(hours=h)).to_numpy()
        test = ((t >= day) & (t < day + DAY)).to_numpy()
        if not test.any():
            continue
        model = make_model().fit(lab[train], y[train])
        out.append(pd.DataFrame({'row': lab.index[test], 'day': day, 'p': model.predict_proba(lab[test])}))
    return pd.concat(out, ignore_index=True)


def run(data: pd.DataFrame, h: int, models: dict, cfg: dict, parts=('val', 'test')) -> pd.DataFrame:
    """All models on the given parts. Returns one row per (part, labelled row): y, day, oblast, p_<model>."""
    ycol = f'y_{h}'
    frames = []
    for part in parts:
        fd = days(cfg, part)
        preds = None
        for name, make in models.items():
            t0 = time.time()
            p = walk_forward(data, h, fd, make).set_index('row')
            logger.info(f'h={h} {part} {name}: {len(p):,} rows, {time.time() - t0:.1f} s')
            if preds is None:
                preds = p[['day']].copy()
            preds[f'p_{name}'] = p['p']
        preds['part'] = part
        src = data.loc[preds.index]
        preds['y'] = src[ycol].astype(int)
        for c in ['t', 'unit_id', 'oblast']:
            preds[c] = src[c]
        frames.append(preds)
    return pd.concat(frames)
