"""Unit-level alert intervals (stage 2; D11, D12, D16). Pure functions: nothing is written here.

One table, two levels:
  segment  maximal union of overlapping or touching source records of a unit (clones, D07;
           overlaps, D11). Segments are the as-of truth for "is the unit under alert at t".
  episode  segments separated by pauses <= pause_merge_min (D12). An episode is the alert the
           target counts. Merging a pause needs the next start, so the episode END and the
           "under alert" state inside a bridged pause come from the future (D16): never read
           them as of t; use alerts.history.AlertHistory instead.

`end_utc` is the recorded end. What a real-time observer saw is a separate table, `seen`
(build_seen): an invented end start + 1 h is written only at the next start (alerts.processor),
and an alert open longer than history.max_open_hours stops counting as active (D16, D19).
AlertHistory reads the state from `seen`, never from end_utc.
"""
import logging

import numpy as np
import pandas as pd

from alerts.mask import UNCERTAIN_REASONS
from alerts.scope import attach_units
from alerts.spans import merge_labels, overlaps, union
from alerts.timeutil import to_sec

logger = logging.getLogger(__name__)

INTERVAL_COLUMNS = ['unit_id', 'start_utc', 'end_utc', 'uncertain', 'episode', 'n_records']
SEEN_COLUMNS = ['unit_id', 'start', 'end']


def build_intervals(scope: pd.DataFrame, units: pd.DataFrame, masks: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Segments of every unit with an episode id.

    `uncertain`: the segment overlaps a mask of rules (a), (b) or (d), so its end is unreliable.
    The flag is retrospective (it depends on the future) and must not become a feature.
    """
    rec = attach_units(scope, units)[['unit_id', 'started_at', 'finished_at']]
    rec = rec.sort_values(['unit_id', 'started_at', 'finished_at']).reset_index(drop=True)
    rec['uncertain'] = _overlaps_masks(rec, masks)

    seg_id = merge_labels(rec, 'unit_id', 'started_at', 'finished_at')
    seg = (rec.groupby(seg_id)
              .agg(unit_id=('unit_id', 'first'), start_utc=('started_at', 'min'),
                   end_utc=('finished_at', 'max'), uncertain=('uncertain', 'any'),
                   n_records=('unit_id', 'size'))
              .reset_index(drop=True))

    pause = pd.Timedelta(minutes=cfg['thresholds']['pause_merge_min'])
    seg['episode'] = merge_labels(seg, 'unit_id', 'start_utc', 'end_utc', gap=pause)

    logger.info(f'{len(rec):,} records -> {len(seg):,} segments -> {seg["episode"].nunique():,} episodes')
    return seg[INTERVAL_COLUMNS]


def build_seen(scope: pd.DataFrame, units: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Intervals during which a real-time observer saw each unit under alert (D16, D19).

    Per source record: from its start until `open_until` (an invented end keeps the alert open
    until the next start), but at most history.max_open_hours: an alert without an all-clear for
    that long stops counting as active (PLAN default for alerts with an unknown end). Both rules
    depend only on the start and on whether an all-clear had been seen, so they are causal.
    The cap is applied per record, before the union: a unit made of several raions (Donetsk) can
    legitimately stay under alert for days through overlapping records.
    """
    rec = attach_units(scope, units)
    cap = rec['started_at'] + pd.Timedelta(hours=cfg['history']['max_open_hours'])
    end = rec['open_until'].where(rec['open_until'] <= cap, cap)
    return union(pd.DataFrame({'unit_id': rec['unit_id'], 'start': rec['started_at'], 'end': end}),
                 'unit_id')[SEEN_COLUMNS]


def episodes(intervals: pd.DataFrame) -> pd.DataFrame:
    """Episode table (unit_id, start_utc, end_utc, uncertain): the PLAN stage 2 contract."""
    return (intervals.groupby('episode', sort=True)
                     .agg(unit_id=('unit_id', 'first'), start_utc=('start_utc', 'min'),
                          end_utc=('end_utc', 'max'), uncertain=('uncertain', 'any'))
                     .reset_index(drop=True))


def _overlaps_masks(rec: pd.DataFrame, masks: pd.DataFrame) -> np.ndarray:
    relevant = union(masks[masks['reason'].isin(UNCERTAIN_REASONS)], 'unit_id')
    by_unit = {u: (to_sec(g['start']), to_sec(g['end'])) for u, g in relevant.groupby('unit_id')}
    flag = np.zeros(len(rec), dtype=bool)
    for u, idx in rec.groupby('unit_id').indices.items():
        if u in by_unit:
            r = rec.iloc[idx]
            flag[idx] = overlaps(to_sec(r['started_at']), to_sec(r['finished_at']), *by_unit[u])
    return flag
