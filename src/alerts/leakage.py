"""Leakage check (PLAN stage 4, D18): corrupt everything after a cut, rebuild, compare forecasts at the cut.

Corruption keeps the start times of future records (the density of channel events, so that outage
detection sees the same activity) and shuffles everything else among them: locations, levels and
durations. Alerts open at the cut get a random end after the cut. Then every table is rebuilt from
the corrupted records, models are fitted on rows with t <= cut - h and predict the rows at t = cut.

Must be equal bit for bit: the units table, the training rows with their labels and all features,
the features and forecasts of the rows at t = cut. The set of rows at t = cut itself may differ
by rows inside a bridged pause (D12: bridging a pause needs the next start); they are reported.

Corruption cannot see leaks made by the source itself: a record written later than its own
timestamps (the invented end start + 1 h appears only at the next start, D16). knowledge_check
covers them: it replays what the dataset contained at the cut (known_at) and requires every feature
of the last days before the cut to be equal to the features computed from the full data (D21).
"""
import numpy as np
import pandas as pd

from alerts.features import NUMERIC, FeatureBuilder
from alerts.pipeline import alert_history, build_tables, model_data
from alerts.processor import flag_records

LOCATION = ['oblast', 'raion', 'hromada', 'level']


def corrupt_after(df: pd.DataFrame, cut: pd.Timestamp, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    out = df.copy().reset_index(drop=True)
    future = np.flatnonzero((out['started_at'] > cut).to_numpy())
    perm = rng.permutation(future)
    cols = [c for c in LOCATION if c in out.columns]
    out.loc[future, cols] = out.loc[perm, cols].to_numpy()
    durations = pd.to_timedelta(out.loc[perm, 'duration'].to_numpy(), unit='s')
    out.loc[future, 'finished_at'] = out.loc[future, 'started_at'] + durations
    open_at_cut = ((out['started_at'] <= cut) & (out['finished_at'] > cut)).to_numpy()
    out.loc[open_at_cut, 'finished_at'] = cut + pd.to_timedelta(rng.integers(1, 48 * 3600, open_at_cut.sum()), unit='s')
    out['duration'] = (out['finished_at'] - out['started_at']).dt.total_seconds()
    return out


def known_at(df: pd.DataFrame, cut: pd.Timestamp, cfg: dict) -> pd.DataFrame:
    """The records as the dataset contained them at `cut`.

    A record exists once it has been written: at its all-clear, or for an invented end at the next
    start of its location. Records started by the cut but not yet written were open alerts; they are
    kept with the end cut + 1 s, which is "still open at the cut" without adding a far-future event
    (that would create a fake channel outage after the last real event).
    """
    key = [c for c in LOCATION if c in df.columns]
    rec = df.copy()
    for c in key:
        rec[c] = rec[c].astype(object).where(rec[c].notna(), '')     # groupby must not drop NaN keys
    rec = flag_records(rec, cfg, key)
    written = rec['next_start'].where(rec['is_fake_end'], rec['finished_at'])
    out = df.loc[(rec['started_at'] <= cut).to_numpy()].copy()
    still_open = (written[out.index] > cut).to_numpy()
    out.loc[still_open, 'finished_at'] = cut + pd.Timedelta(seconds=1)
    out['duration'] = (out['finished_at'] - out['started_at']).dt.total_seconds()
    return out.reset_index(drop=True)


def knowledge_check(df: pd.DataFrame, cfg: dict, cut: pd.Timestamp, units: pd.DataFrame | None = None,
                    neighbors: pd.DataFrame | None = None, days: int = 7) -> dict:
    """Features of the grid rows in (cut - days, cut] from the full data and from known_at(cut) must match."""
    full = build_tables(df, cfg, units, neighbors)
    known_df = known_at(df, cut, cfg)
    known = build_tables(known_df, cfg, full.units, full.neighbors)
    rows = full.grid[(full.grid['t'] > cut - pd.Timedelta(days=days)) & (full.grid['t'] <= cut)]
    rows = rows[['unit_id', 't']].reset_index(drop=True)
    f_full = FeatureBuilder(alert_history(full), full.units, full.neighbors, cfg).build(rows)
    f_known = FeatureBuilder(alert_history(known), full.units, full.neighbors, cfg).build(rows)
    pd.testing.assert_frame_equal(f_full, f_known, check_exact=True, obj=f'features known at {cut}')
    return {'cut': str(cut), 'rows': len(rows), 'open_at_cut': int((known_df['finished_at'] > cut).sum())}


def forecasts_at(data: pd.DataFrame, cut: pd.Timestamp, h: int, models: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Training rows (keys, label, features) for the forecast at `cut`, and forecasts for rows at t = cut."""
    ycol = f'y_{h}'
    train = data[(data['t'] <= cut - pd.Timedelta(hours=h)) & data[ycol].notna()]
    target = data[data['t'] == cut].sort_values('unit_id')
    out = target[['unit_id'] + NUMERIC].copy()
    for name, make in models.items():
        out[f'p_{name}'] = make().fit(train, train[ycol].to_numpy(dtype=float)).predict_proba(target)
    key = train[['unit_id', 't', ycol] + NUMERIC].sort_values(['t', 'unit_id']).reset_index(drop=True)
    return key, out.reset_index(drop=True)


def check(df: pd.DataFrame, cfg: dict, cut: pd.Timestamp, h: int, models: dict,
          units: pd.DataFrame | None = None, neighbors: pd.DataFrame | None = None, seed: int = 0) -> dict:
    """Run the comparison; raise AssertionError with a description on any difference."""
    clean = build_tables(df, cfg, units, neighbors)
    bad = build_tables(corrupt_after(df, cut, seed), cfg, units, neighbors)
    if units is None:
        pd.testing.assert_frame_equal(clean.units, bad.units, obj='units (clone detection uses the train period)')
    train_a, fc_a = forecasts_at(model_data(clean, cfg), cut, h, models)
    train_b, fc_b = forecasts_at(model_data(bad, cfg), cut, h, models)
    pd.testing.assert_frame_equal(train_a, train_b, obj='training rows, labels and features')
    common = sorted(set(fc_a['unit_id']) & set(fc_b['unit_id']))
    if not common:
        raise AssertionError('no common rows at the cut')
    pick = lambda fc: fc[fc['unit_id'].isin(common)].reset_index(drop=True)  # noqa: E731
    pd.testing.assert_frame_equal(pick(fc_a), pick(fc_b), check_exact=True, obj='features and forecasts at the cut')
    after = [a.grid[a.grid['t'] > cut].reset_index(drop=True) for a in (clean, bad)]
    return {'cut': str(cut), 'h': h, 'training_rows': len(train_a), 'rows_at_cut': len(common),
            'rows_at_cut_only_one_version': len(set(fc_a['unit_id']) ^ set(fc_b['unit_id'])),
            'future_changed': not after[0].equals(after[1])}   # the check is not vacuous
