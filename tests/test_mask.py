import pandas as pd
from conftest import records, units_table, utc

from alerts.intervals import build_intervals
from alerts.mask import FAKE_END, LONG, OUTAGE, build_masks
from alerts.scope import select_scope

UNITS = units_table([
    ('A', 'Raion 1', 'U_A'),
    ('A', 'Raion 2', 'U_A'),  # clone of Raion 1
    ('B', 'Raion 3', 'U_B'),
])


def run(rows, cfg):
    df = records(rows)
    masks, outages, stats = build_masks(df, select_scope(df, cfg, period=False), UNITS, cfg)
    intervals = build_intervals(select_scope(df, cfg), UNITS, masks, cfg)
    return masks, outages, intervals


def test_long_alert_goes_to_mask(cfg):
    """Rule (a): an alert longer than 24 h is masked whole, on its unit, and flagged uncertain."""
    rows = [
        ('A', 'Raion 1', 'raion', '2026-01-10T08:00:00Z', '2026-01-11T14:00:00Z'),  # 30 h
        ('A', 'Raion 2', 'raion', '2026-01-10T08:00:05Z', '2026-01-10T09:00:00Z'),  # its clone, normal end
        ('B', 'Raion 3', 'raion', '2026-01-10T08:00:00Z', '2026-01-11T07:59:59Z'),  # 23:59:59: no mask
    ]
    masks, _, intervals = run(rows, cfg)
    long = masks[masks['reason'] == LONG]
    assert long[['unit_id', 'start', 'end']].values.tolist() == [
        ['U_A', utc('2026-01-10T08:00:00Z'), utc('2026-01-11T14:00:00Z')]]
    assert intervals.set_index('unit_id')['uncertain'].to_dict() == {'U_A': True, 'U_B': False}


def test_fake_end_goes_to_mask(cfg):
    """Rule (b): exactly 1 h and the next start of the same source location more than 3 h later.

    The mask runs from the start to that next start; the next alert itself is not uncertain.
    """
    rows = [
        # fake end: next start of Raion 3 is 5 h after this start
        ('B', 'Raion 3', 'raion', '2026-01-10T08:00:00Z', '2026-01-10T09:00:00Z'),
        ('B', 'Raion 3', 'raion', '2026-01-10T13:00:00Z', '2026-01-10T13:40:00Z'),
        # exactly 1 h, but the next start comes after 2 h: a real end
        ('B', 'Raion 3', 'raion', '2026-01-12T08:00:00Z', '2026-01-12T09:00:00Z'),
        ('B', 'Raion 3', 'raion', '2026-01-12T10:00:00Z', '2026-01-12T10:30:00Z'),
        # 3599 s: not the processor's value
        ('B', 'Raion 3', 'raion', '2026-01-14T08:00:00Z', '2026-01-14T08:59:59Z'),
        ('B', 'Raion 3', 'raion', '2026-01-14T20:00:00Z', '2026-01-14T20:30:00Z'),
        # the processor works per source location: the clone's start 1 h later does not matter,
        # Raion 1's own next start is 4 h later
        ('A', 'Raion 1', 'raion', '2026-01-16T08:00:00Z', '2026-01-16T09:00:00Z'),
        ('A', 'Raion 2', 'raion', '2026-01-16T09:00:00Z', '2026-01-16T09:20:00Z'),
        ('A', 'Raion 1', 'raion', '2026-01-16T12:00:00Z', '2026-01-16T12:30:00Z'),
    ]
    masks, _, intervals = run(rows, cfg)
    fake = masks[masks['reason'] == FAKE_END].sort_values('unit_id')
    assert fake[['unit_id', 'start', 'end']].values.tolist() == [
        ['U_A', utc('2026-01-16T08:00:00Z'), utc('2026-01-16T12:00:00Z')],
        ['U_B', utc('2026-01-10T08:00:00Z'), utc('2026-01-10T13:00:00Z')],
    ]
    flagged = intervals.loc[intervals['uncertain'], 'start_utc'].tolist()
    assert flagged == [utc('2026-01-16T08:00:00Z'), utc('2026-01-10T08:00:00Z')]


def test_channel_outage_masks_every_unit(cfg):
    """Rule (d): a silence of the whole channel is masked for all units, including quiet ones."""
    cfg['thresholds']['outage_gap_hours'] = 6
    hours = pd.date_range('2026-01-10T00:00:00Z', '2026-01-12T00:00:00Z', freq='h')
    hours = hours[(hours < utc('2026-01-11T02:00:00Z')) | (hours > utc('2026-01-11T12:00:00Z'))]
    rows = [('B', 'Raion 3', 'raion', t, t + pd.Timedelta(minutes=10)) for t in hours]
    rows.append(('A', 'Raion 1', 'raion', '2026-01-10T05:00:00Z', '2026-01-10T05:30:00Z'))
    masks, outages, _ = run(rows, cfg)
    assert outages.values.tolist() == [[utc('2026-01-11T01:10:00Z'), utc('2026-01-11T13:00:00Z')]]
    out = masks[masks['reason'] == OUTAGE]
    assert sorted(out['unit_id']) == ['U_A', 'U_B']
    assert (out['start'] == utc('2026-01-11T01:10:00Z')).all()
