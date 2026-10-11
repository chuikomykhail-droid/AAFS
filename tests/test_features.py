import numpy as np
import pandas as pd
from conftest import records, units_table, utc
from test_leakage import NEIGHBORS

from alerts.features import FeatureBuilder
from alerts.intervals import build_intervals, build_seen
from alerts.mask import MASK_COLUMNS, OUTAGE
from alerts.scope import select_scope

UNITS = units_table([('A', 'Raion 1', 'U_A'), ('A', 'Raion 2', 'U_A'), ('B', 'Raion 3', 'U_B'),
                     ('B', 'Raion 4', 'U_C'), ('C', 'Raion 5', 'U_D')])


def features(rows, cfg, at, units, masks=None):
    masks = pd.DataFrame(columns=MASK_COLUMNS) if masks is None else masks
    scope = select_scope(records(rows), cfg)
    fb = FeatureBuilder(build_seen(scope, UNITS, cfg), build_intervals(scope, UNITS, masks, cfg),
                        UNITS, masks, NEIGHBORS, cfg)
    grid = pd.DataFrame({'unit_id': units, 't': [utc(x) for x in at]})
    return fb.build(grid)


def test_hand_computed_values(cfg):
    rows = [('B', 'Raion 3', 'raion', '2026-01-10T09:30:00Z', '2026-01-10T10:30:00Z'),   # U_B, oblast B
            ('C', 'Raion 5', 'raion', '2026-01-09T12:00:00Z', '2026-01-09T13:00:00Z')]   # U_D, a day before
    f = features(rows, cfg, ['2026-01-10T10:00:00Z'] * 3 + ['2026-01-10T12:00:00Z'],
                 ['U_C', 'U_A', 'U_D', 'U_B'])
    c, a, d, b = (f.iloc[i] for i in range(4))
    assert c['oblast_active_share'] == 1.0            # the other unit of oblast B is under alert
    assert c['neighbor_units_active_share'] == 0.5    # U_B of {U_B, U_D}
    assert a['neighbor_units_active_share'] == 1.0    # U_B of {U_B}
    assert np.isnan(a['oblast_active_share'])         # U_A is the only unit of oblast A
    assert a['neighbor_oblasts_active_share'] == 1.0  # oblast B of {B}
    assert c['neighbor_oblasts_active_share'] == 0.0  # neither A nor C
    assert c['oblasts_active'] == 1 and c['country_starts_60m'] == 1
    assert c['country_starts_30m'] == 0               # the start at 09:30 is on the open edge of (09:30, 10:00]
    assert c['neighbor_starts_60m'] == 1 and a['oblast_starts_60m'] == 0
    assert np.isclose(d['since_end_log_h'], np.log1p(21.0))         # ended 21 h ago
    assert d['starts_24h'] == 1 and d['starts_6h'] == 0
    assert np.isclose(b['since_end_log_h'], np.log1p(1.5))
    assert np.isclose(b['active_share_24h'], 1 / 24, atol=1e-6)
    assert np.isnan(c['since_end_log_h'])                          # U_C has never been under alert
    assert c['hour_kyiv'] == 12 and c['dow_kyiv'] == 5             # 10:00 UTC on Saturday = 12:00 in Kyiv
    assert f['lookback_ok'].all()


def test_outage_rules(cfg):
    """D19: no rows within 24 h after an outage; 7-day counts scaled to observed time; observed time since end."""
    rows = [('B', 'Raion 3', 'raion', '2026-01-10T00:00:00Z', '2026-01-10T00:50:00Z'),
            ('B', 'Raion 3', 'raion', '2026-01-13T00:00:00Z', '2026-01-13T00:30:00Z')]
    outage = pd.DataFrame({'unit_id': ['U_A', 'U_B', 'U_C', 'U_D'], 'start': utc('2026-01-11T00:00:00Z'),
                           'end': utc('2026-01-12T00:00:00Z'), 'reason': OUTAGE})
    f = features(rows, cfg, ['2026-01-11T12:00:00Z', '2026-01-12T12:00:00Z', '2026-01-13T12:00:00Z'],
                 ['U_B'] * 3, outage)
    assert f['lookback_ok'].tolist() == [False, False, True]
    # at 13.01 12:00 the week (06.01 12:00, 13.01 12:00] has 6 observed days and 2 starts -> 2 * 7/6
    assert np.isclose(f.iloc[2]['starts_7d'], 2 * 7 / 6, rtol=1e-6)
    # at 12.01 12:00 the last end was 10.01 00:50: 59 h 10 min ago, 24 h of them in the outage
    assert np.isclose(f.iloc[1]['since_end_log_h'], np.log1p(35 + 1 / 6))
