import numpy as np
import pandas as pd
from conftest import records, units_table, utc

from alerts.grid import build_grid
from alerts.intervals import build_intervals, build_seen
from alerts.mask import OUTAGE, build_masks
from alerts.scope import select_scope

UNITS = units_table([('A', 'Raion 1', 'U_A'), ('B', 'Raion 3', 'U_B')])


def run(rows, cfg, extra_masks=None):
    df = records(rows)
    masks, _, _ = build_masks(df, select_scope(df, cfg, period=False), UNITS, cfg)
    if extra_masks is not None:
        masks = pd.concat([masks, extra_masks], ignore_index=True)
    scope = select_scope(df, cfg)
    iv = build_intervals(scope, UNITS, masks, cfg)
    return build_grid(build_seen(scope, UNITS, cfg), iv, masks, UNITS, cfg)


def row(grid, unit, t):
    r = grid[(grid['unit_id'] == unit) & (grid['t'] == utc(t))]
    return None if r.empty else r.iloc[0]


def b(start, end):
    return ('B', 'Raion 3', 'raion', start, end)


def test_plan_example_and_horizons(cfg):
    """PLAN: quiet at 14:00, an alert starts at 15:30 -> y_1 = 0, y_3 = 1, y_6 = 1."""
    grid, _ = run([b('2026-01-10T15:30:00Z', '2026-01-10T16:00:00Z')], cfg)
    r = row(grid, 'U_B', '2026-01-10T14:00:00Z')
    assert (r['y_1'], r['y_3'], r['y_6']) == (0, 1, 1)
    assert row(grid, 'U_B', '2026-01-10T15:00:00Z')['y_1'] == 1
    assert row(grid, 'U_B', '2026-01-10T16:00:00Z') is not None     # the all-clear came at 16:00
    assert grid['t'].min() == utc(cfg['periods']['warmup_end'])      # no rows in the warm-up week


def test_bridged_pause_and_held_open_have_no_rows(cfg):
    rows = [b('2026-01-10T10:00:00Z', '2026-01-10T10:50:00Z'),
            b('2026-01-10T11:05:00Z', '2026-01-10T12:00:00Z'),      # pause of 15 min bridged (D12)
            b('2026-01-12T10:00:00Z', '2026-01-12T11:00:00Z'),      # exactly 1 h, next start 2.5 h later:
            b('2026-01-12T12:30:00Z', '2026-01-12T13:00:00Z')]      # no mask (b), but no all-clear seen
    grid, st = run(rows, cfg)
    assert row(grid, 'U_B', '2026-01-10T11:00:00Z') is None
    assert row(grid, 'U_B', '2026-01-12T11:00:00Z') is None          # recorded end at 11:00, still open
    assert row(grid, 'U_B', '2026-01-12T12:00:00Z') is None
    assert st['status']['bridged_pause']['train'] == 1
    assert st['status']['held_open']['train'] == 2


def test_masks(cfg):
    rows = [
        # rule (b): exactly 1 h, next start 5 h later -> mask (08:00, 13:00)
        b('2026-01-12T08:00:00Z', '2026-01-12T09:00:00Z'),
        b('2026-01-12T13:00:00Z', '2026-01-12T13:20:00Z'),
        # rule (a): 30 h
        b('2026-01-15T08:00:00Z', '2026-01-16T14:00:00Z'),
    ]
    outage = pd.DataFrame({'unit_id': ['U_A', 'U_B'], 'start': utc('2026-01-20T10:30:00Z'),
                           'end': utc('2026-01-20T20:00:00Z'), 'reason': OUTAGE})
    grid, st = run(rows, cfg, outage)

    for h in ['10', '11', '12']:                                     # inside mask (b): no rows
        assert row(grid, 'U_B', f'2026-01-12T{h}:00:00Z') is None
    r = row(grid, 'U_B', '2026-01-12T07:00:00Z')                     # window reaches mask (b): label kept
    assert (r['y_1'], r['y_3']) == (1, 1)
    r = row(grid, 'U_B', '2026-01-15T06:00:00Z')                     # window reaches mask (a): label kept
    assert (r['y_1'], r['y_3']) == (0, 1)

    r = row(grid, 'U_A', '2026-01-20T08:00:00Z')                     # window reaches the outage
    assert r['y_1'] == 0 and pd.isna(r['y_3']) and pd.isna(r['y_6'])
    assert pd.isna(row(grid, 'U_A', '2026-01-20T10:00:00Z')['y_1'])
    assert row(grid, 'U_A', '2026-01-20T15:00:00Z') is None
    assert row(grid, 'U_A', '2026-01-20T20:00:00Z')['y_6'] == 0

    # right edge: a row exists only while t + h <= data_end
    r = row(grid, 'U_A', '2026-02-28T21:00:00Z')
    assert r['y_3'] == 0 and pd.isna(r['y_6'])
    assert row(grid, 'U_A', '2026-02-28T23:00:00Z')['y_1'] == 0
    assert grid['t'].max() == utc('2026-02-28T23:00:00Z')
    assert st['horizons'][3]['reach_known_mask'] == 4               # 06, 07 before (b) and before (a)


def test_labels_are_monotone_in_h(cfg):
    rng = np.random.default_rng(1)
    rows = []
    for _ in range(300):
        s = utc('2026-01-02T00:00:00Z') + pd.Timedelta(seconds=int(rng.integers(0, 55 * 86400)))
        rows.append(('A' if rng.random() < .5 else 'B', 'Raion 1' if rng.random() < .5 else 'Raion 3', 'raion',
                     s, s + pd.Timedelta(seconds=int(rng.integers(300, 3 * 3600)))))
    rows = [r for r in rows if (r[0], r[1]) in {('A', 'Raion 1'), ('B', 'Raion 3')}]
    grid, _ = run(rows, cfg)
    y1, y3, y6 = (grid[f'y_{h}'].astype('float') for h in (1, 3, 6))
    assert (y1[y3.notna()] <= y3[y3.notna()]).all() and (y3[y6.notna()] <= y6[y6.notna()]).all()
    assert y1.notna().all() and 0 < y3.mean() < 1
