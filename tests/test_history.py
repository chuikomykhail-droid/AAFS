import numpy as np
import pandas as pd
from conftest import records, units_table, utc

from alerts.history import AlertHistory
from alerts.intervals import build_intervals
from alerts.mask import MASK_COLUMNS
from alerts.scope import select_scope

NO_MASKS = pd.DataFrame(columns=MASK_COLUMNS)
UNITS = units_table([('A', 'Raion 1', 'U_A'), ('A', 'Raion 2', 'U_A'), ('B', 'Raion 3', 'U_B')])
H = pd.Timedelta(hours=1)


def history(rows, cfg):
    iv = build_intervals(select_scope(records(rows), cfg), UNITS, NO_MASKS, cfg)
    return AlertHistory(iv, ['U_A', 'U_B'])


def test_bridged_pause_is_quiet_as_of_t(cfg):
    """D12 bridges the 15-min pause into one episode, but at 11:00 nobody knew the 11:05 start."""
    rows = [('B', 'Raion 3', 'raion', '2026-01-10T10:00:00Z', '2026-01-10T10:50:00Z'),
            ('B', 'Raion 3', 'raion', '2026-01-10T11:05:00Z', '2026-01-10T12:00:00Z')]
    h = history(rows, cfg)
    T = pd.DatetimeIndex([utc('2026-01-10T10:30:00Z'), utc('2026-01-10T11:00:00Z'), utc('2026-01-10T11:30:00Z')])
    assert h.active(T)[:, 1].tolist() == [True, False, True]
    assert h.seconds_since_end(T)[1, 1] == 10 * 60
    assert h.starts(T, 3 * H)[:, 1].tolist() == [1, 1, 1]          # one episode, counted from its start
    assert h.seconds_active(T, 3 * H)[:, 1].tolist() == [30 * 60, 50 * 60, 75 * 60]


def test_corrupting_the_future_changes_nothing(cfg):
    """Rebuild intervals after replacing every timestamp later than t with noise: answers at <= t stay."""
    rng = np.random.default_rng(0)
    t0, locs = utc('2026-01-05T00:00:00Z'), [('A', 'Raion 1'), ('A', 'Raion 2'), ('B', 'Raion 3')]
    rows = []
    for _ in range(400):
        ob, ra = locs[rng.integers(3)]
        s = t0 + pd.Timedelta(seconds=int(rng.integers(0, 20 * 86400)))
        rows.append((ob, ra, 'raion', s, s + pd.Timedelta(seconds=int(rng.integers(60, 4 * 3600)))))
    t = utc('2026-01-15T12:00:00Z')

    def noise():
        return t + pd.Timedelta(seconds=int(rng.integers(1, 5 * 86400)))

    corrupted = []
    for ob, ra, lvl, s, e in rows:
        if s > t:
            s = noise()
            e = s + pd.Timedelta(seconds=int(rng.integers(1, 86400)))
        elif e > t:
            e = noise()
        corrupted.append((ob, ra, lvl, s, e))

    T = pd.date_range(t - pd.Timedelta(days=3), t, freq='17min')
    a, b = history(rows, cfg), history(corrupted, cfg)
    assert a.active(T).any() and a.starts(T, 6 * H).any()        # the check is not vacuous
    np.testing.assert_array_equal(a.active(T), b.active(T))
    np.testing.assert_array_equal(a.seconds_since_end(T), b.seconds_since_end(T))
    for w in [H, 6 * H, 24 * H]:
        np.testing.assert_array_equal(a.starts(T, w), b.starts(T, w))
        np.testing.assert_array_equal(a.seconds_active(T, w), b.seconds_active(T, w))
