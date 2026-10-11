"""Mask of "status unknown" (D10, D13, D15). Pure functions: nothing is written to disk here.

Rules, all evaluated retrospectively (they use the future, so they are target-side only):
  (a) long_24h       alert longer than long_alert_hours: the alert itself;
  (b) fake_1h        processor-invented end (exactly fake_end_duration_s, next start of the same
                     source location more than fake_end_next_start_h later): (start, next_start);
  (c) after_data_end everything from data_end to the end of the file;
  (d) outage         channel silence: no event of any record for more than outage_gap_hours.
Rules (a) and (b) are applied to source locations (the processor works per location) and then
moved to units; (c) and (d) apply to every unit.

The mask table keeps one row per (unit, reason, merged interval): intervals are disjoint within a
reason but may overlap across reasons. Use spans.union() for the total masked time.
"""
import pandas as pd

from alerts.config import ts
from alerts.scope import ROLE_TARGET, attach_units
from alerts.spans import clipped_seconds, union

LONG = 'long_24h'
FAKE_END = 'fake_1h'
AFTER_END = 'after_data_end'
OUTAGE = 'outage'
REASONS = [LONG, FAKE_END, AFTER_END, OUTAGE]
# Reasons that make an alert's own end unreliable (`uncertain` flag in intervals)
UNCERTAIN_REASONS = [LONG, FAKE_END, OUTAGE]

MASK_COLUMNS = ['unit_id', 'start', 'end', 'reason']


def detect_outages(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """D15: silences of the whole channel inside [work_start, data_end).

    Events are the starts and ends of every record in the file, at any level and in any oblast:
    while the channel posts, some event appears every few hours (longest normal gap is 3.7 h).
    Returns columns start (last event before the gap), end (first event after it).
    """
    work_start, data_end = ts(cfg['periods']['work_start']), ts(cfg['data_end'])
    min_gap = pd.Timedelta(hours=cfg['thresholds']['outage_gap_hours'])
    events = pd.concat([df['started_at'], df['finished_at']]).sort_values().drop_duplicates()
    events = events.reset_index(drop=True)
    gap = events.diff()
    i = gap.index[gap > min_gap]
    out = pd.DataFrame({'start': events[i - 1].reset_index(drop=True),
                        'end': events[i].reset_index(drop=True)})
    return out[(out['start'] < data_end) & (out['end'] > work_start)].reset_index(drop=True)


def build_masks(df: pd.DataFrame, scope_all: pd.DataFrame, units: pd.DataFrame, cfg: dict
                ) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Build the mask table.

    df: the whole cleaned file (outage detection and the end of the file);
    scope_all: select_scope(..., period=False), so that next starts outside the period are seen.
    Returns (masks, outages, stats).
    """
    work_start, data_end = ts(cfg['periods']['work_start']), ts(cfg['data_end'])
    in_period = lambda m: m[(m['start'] < data_end) & (m['end'] > work_start)]

    rec = attach_units(scope_all, units)  # processor flags come from select_scope (alerts.processor)
    rule_a = rec[rec['is_long']]
    rule_b = rec[rec['is_fake_end']]

    loc_masks = pd.concat([
        pd.DataFrame({'unit_id': rule_a['unit_id'], 'start': rule_a['started_at'],
                      'end': rule_a['finished_at'], 'reason': LONG, 'role': rule_a['role']}),
        pd.DataFrame({'unit_id': rule_b['unit_id'], 'start': rule_b['started_at'],
                      'end': rule_b['next_start'], 'reason': FAKE_END, 'role': rule_b['role']}),
    ], ignore_index=True)
    loc_masks = in_period(loc_masks)

    outages = detect_outages(df, cfg)
    file_end = max(df['finished_at'].max(), data_end)  # never a negative interval
    all_units = units['unit_id'].drop_duplicates()
    global_masks = [pd.DataFrame({'unit_id': all_units, 'start': data_end, 'end': file_end, 'reason': AFTER_END})]
    global_masks += [pd.DataFrame({'unit_id': all_units, 'start': o.start, 'end': o.end, 'reason': OUTAGE})
                     for o in outages.itertuples()]

    parts = [union(g, 'unit_id').assign(reason=reason)
             for reason, g in pd.concat([loc_masks[MASK_COLUMNS]] + global_masks).groupby('reason')]
    masks = pd.concat(parts, ignore_index=True)[MASK_COLUMNS]
    masks['start'] = masks['start'].dt.as_unit('s')
    masks['end'] = masks['end'].dt.as_unit('s')
    masks = masks.sort_values(['unit_id', 'start', 'reason']).reset_index(drop=True)

    stats = _stats(loc_masks, masks, units, outages, cfg)
    return masks, outages, stats


def _stats(loc_masks: pd.DataFrame, masks: pd.DataFrame, units: pd.DataFrame,
           outages: pd.DataFrame, cfg: dict) -> dict:
    """Counts per rule (source locations and units) and masked share of target unit-hours per part."""
    p = cfg['periods']
    bounds = {'train': (ts(p['work_start']), ts(p['train_end'])),
              'val': (ts(p['train_end']), ts(p['val_end'])),
              'test': (ts(p['val_end']), ts(cfg['data_end']))}
    test_start = bounds['test'][0]
    target_ids = set(units.loc[units['role'] == ROLE_TARGET, 'unit_id'])
    n_target = len(target_ids)

    stats = {'outages': outages.to_dict('records')}
    for reason in [LONG, FAKE_END]:
        lm = loc_masks[(loc_masks['reason'] == reason) & (loc_masks['role'] == ROLE_TARGET)]
        um = masks[(masks['reason'] == reason) & masks['unit_id'].isin(target_ids)]
        stats[reason] = {'locations': len(lm), 'locations_test': int((lm['start'] >= test_start).sum()),
                         'units': len(um), 'units_test': int((um['start'] >= test_start).sum())}

    target = masks[masks['unit_id'].isin(target_ids)]
    share = {}
    for name, sel in [(r, target[target['reason'] == r]) for r in [LONG, FAKE_END, OUTAGE]] + [('total', target)]:
        total = union(sel, 'unit_id')
        share[name] = {part: clipped_seconds(total['start'], total['end'], lo, hi)
                       / (n_target * (hi - lo).total_seconds()) * 100
                       for part, (lo, hi) in bounds.items()}
    stats['masked_pct'] = share
    return stats
