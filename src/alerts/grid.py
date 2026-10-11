"""Stage 3: hourly grid of (unit, t) and binary targets (PLAN stage 3; D10, D12, D16, D17).

A row exists for a target unit at an hourly moment t in [warmup_end, data_end) when the unit is
quiet at t. The status of every candidate (unit, t) is decided in this order:
  alert          inside an episode by the recorded segments;
  bridged_pause  inside an episode only because a pause <= pause_merge_min was bridged (D12);
  masked_*       inside a mask: outage (d), after_data_end (c), long_24h (a), fake_1h (b);
  held_open      quiet by the records, but no all-clear had been seen yet (AlertHistory, D16):
                 a real-time observer would not have asked for a forecast;
  quiet          a row.

y_h = 1 if an episode of the unit starts in (t, t+h]. y_h is missing (NA) when the window
(t, t+h) reaches a mask whose start is not an event: (c) after data_end or (d) an outage; this
selection depends on time only, not on the outcome. Windows that reach a mask of rule (a) or (b)
keep their label: such a mask starts with a real alert start, so y_h = 1 is known (D10).
"""
import numpy as np
import pandas as pd

from alerts.config import ts
from alerts.history import AlertHistory
from alerts.intervals import episodes
from alerts.mask import AFTER_END, FAKE_END, LONG, OUTAGE
from alerts.scope import ROLE_TARGET
from alerts.spans import count_in, covers, reaches, union
from alerts.timeutil import to_sec

STATUSES = ['quiet', 'alert', 'bridged_pause', 'masked_outage', 'masked_after_data_end',
            'masked_long_24h', 'masked_fake_1h', 'held_open']
_MASK_ORDER = [OUTAGE, AFTER_END, LONG, FAKE_END]   # precedence when masks overlap
_UNLABELLED = [AFTER_END, OUTAGE]                    # masks whose start is not an event
_KNOWN_START = [LONG, FAKE_END]                      # masks that start with a real alert start
PARTS = ['train', 'val', 'test']


def moments(cfg: dict) -> pd.DatetimeIndex:
    """Hourly forecast moments from the end of the warm-up week to data_end (exclusive)."""
    return pd.date_range(ts(cfg['periods']['warmup_end']), ts(cfg['data_end']), freq='h', inclusive='left')


def part_of(t: pd.Series, cfg: dict) -> pd.Series:
    """train / val / test by the moment t (D14)."""
    p = cfg['periods']
    edges = [ts(p['warmup_end']), ts(p['train_end']), ts(p['val_end']), ts(cfg['data_end'])]
    # searchsorted, not pd.cut: a part may be empty (another source has no train or val, stage 8)
    k = np.searchsorted(to_sec(pd.DatetimeIndex(edges)), to_sec(t), side='right')
    labels = np.array(['before'] + PARTS + ['after'])
    return pd.Series(labels[k], index=t.index)


def build_grid(seen: pd.DataFrame, intervals: pd.DataFrame, masks: pd.DataFrame, units: pd.DataFrame,
               cfg: dict) -> tuple[pd.DataFrame, dict]:
    """Rows (unit_id, oblast, t, part, y_<h> for every horizon) and the accounting of candidates."""
    horizons = sorted(cfg['horizons'])
    tgt = units[units['role'] == ROLE_TARGET].drop_duplicates('unit_id')[['unit_id', 'oblast']]
    ids = tgt['unit_id'].tolist()
    T = moments(cfg)
    t = to_sec(T)
    data_end = to_sec(ts(cfg['data_end']))
    hsec = {h: h * 3600 for h in horizons}

    ep = episodes(intervals)
    held = AlertHistory(seen, intervals, ids).active(T)
    by_reason = {r: union(g, 'unit_id') for r, g in masks.groupby('reason')}
    unlabelled = union(masks[masks['reason'].isin(_UNLABELLED)], 'unit_id')
    known = union(masks[masks['reason'].isin(_KNOWN_START)], 'unit_id')

    status = np.zeros((len(T), len(ids)), dtype=np.int8)
    starts = {h: np.zeros((len(T), len(ids)), dtype=np.int16) for h in horizons}
    labelled = {h: np.zeros((len(T), len(ids)), dtype=bool) for h in horizons}
    reach_known = {h: np.zeros((len(T), len(ids)), dtype=bool) for h in horizons}

    for j, u in enumerate(ids):
        e = ep[ep['unit_id'] == u]
        es, ee = to_sec(e['start_utc']), to_sec(e['end_utc'])
        g = intervals[intervals['unit_id'] == u]
        in_episode = covers(es, ee, t)
        in_segment = covers(to_sec(g['start_utc']), to_sec(g['end_utc']), t)

        st = np.zeros(len(t), dtype=np.int8)                       # 0 = quiet
        st[held[:, j]] = STATUSES.index('held_open')
        for reason in reversed(_MASK_ORDER):                       # first in the order wins
            m = by_reason.get(reason)
            if m is not None:
                mu = m[m['unit_id'] == u]
                st[covers(to_sec(mu['start']), to_sec(mu['end']), t)] = STATUSES.index(f'masked_{reason}')
        st[in_episode & ~in_segment] = STATUSES.index('bridged_pause')
        st[in_segment] = STATUSES.index('alert')
        status[:, j] = st

        un = unlabelled[unlabelled['unit_id'] == u]
        kn = known[known['unit_id'] == u]
        for h in horizons:
            starts[h][:, j] = count_in(es, t, t + hsec[h])
            labelled[h][:, j] = (~reaches(to_sec(un['start']), to_sec(un['end']), t, t + hsec[h])
                                 & (t + hsec[h] <= data_end))   # 1b.5, also when the file ends early
            reach_known[h][:, j] = reaches(to_sec(kn['start']), to_sec(kn['end']), t, t + hsec[h])

    quiet = status == 0
    ti, uj = np.nonzero(quiet)
    grid = pd.DataFrame({'unit_id': np.array(ids)[uj], 't': T[ti]})
    grid['oblast'] = grid['unit_id'].map(tgt.set_index('unit_id')['oblast'])
    grid['part'] = part_of(grid['t'], cfg)
    for h in horizons:
        y = pd.array((starts[h][ti, uj] > 0).astype('int8'), dtype='Int8')
        y[~labelled[h][ti, uj]] = pd.NA
        grid[f'y_{h}'] = y
    grid = grid.sort_values(['t', 'unit_id'], kind='stable').reset_index(drop=True)

    _check(grid, horizons)
    stats = _stats(grid, status, quiet, starts, labelled, reach_known, T, cfg, horizons)
    return grid, stats


def _check(grid: pd.DataFrame, horizons: list) -> None:
    """y_1 <= y_3 <= y_6 wherever both exist, and a longer window is labelled only if a shorter one is."""
    for a, b in zip(horizons, horizons[1:]):
        ya, yb = grid[f'y_{a}'], grid[f'y_{b}']
        if (yb.notna() & ya.isna()).any():
            raise ValueError(f'y_{b} labelled where y_{a} is not')
        both = ya.notna() & yb.notna()
        if (ya[both] > yb[both]).any():
            raise ValueError(f'y_{a} > y_{b} in some rows')


def _stats(grid, status, quiet, starts, labelled, reach_known, T, cfg, horizons) -> dict:
    part = part_of(pd.Series(T), cfg).to_numpy()
    stats = {'moments': len(T), 'units': status.shape[1], 'candidates': int(status.size)}
    stats['status'] = {s: {p: int((status[part == p] == i).sum()) for p in PARTS}
                       for i, s in enumerate(STATUSES)}
    stats['horizons'] = {}
    for h in horizons:
        y = grid[f'y_{h}']
        lab = labelled[h] & quiet
        rk = reach_known[h] & lab
        pos = starts[h] > 0
        if (rk & ~pos).any():   # D10: such a mask starts with a real alert start, so y must be 1
            raise ValueError(f'h={h}: a window reaching a mask of rule (a)/(b) has y = 0')
        stats['horizons'][h] = {
            'rows': {p: int(y[grid['part'] == p].notna().sum()) for p in PARTS},
            'unlabelled': {p: int((quiet & ~labelled[h])[part == p].sum()) for p in PARTS},
            'positives': {p: int((y[grid['part'] == p] == 1).sum()) for p in PARTS},
            'base_rate': {p: _share(y[grid['part'] == p].dropna().to_numpy(dtype=float)) for p in PARTS},
            'reach_known_mask': int(rk.sum()),
            'multi_start_share': {p: _share(starts[h][lab & pos & (part == p)[:, None]] >= 2) for p in PARTS},
        }
    train = grid[grid['part'] == 'train']
    stats['oblast_train'] = (train.groupby('oblast')
                                  .agg(units=('unit_id', 'nunique'), rows=('t', 'size'),
                                       **{f'base_rate_{h}': (f'y_{h}', 'mean') for h in horizons},
                                       **{f'positives_{h}': (f'y_{h}', 'sum') for h in horizons}))
    return stats


def _share(x: np.ndarray) -> float:
    return float(np.mean(x)) if len(x) else float('nan')
