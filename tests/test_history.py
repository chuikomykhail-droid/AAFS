import numpy as np
import pandas as pd
from conftest import records, units_table, utc

from alerts.history import AlertHistory
from alerts.intervals import build_intervals, build_seen
from alerts.mask import MASK_COLUMNS
from alerts.scope import select_scope

NO_MASKS = pd.DataFrame(columns=MASK_COLUMNS)
UNITS = units_table([('A', 'Raion 1', 'U_A'), ('A', 'Raion 2', 'U_A'), ('B', 'Raion 3', 'U_B')])
H = pd.Timedelta(hours=1)


def history(rows, cfg):
    scope = select_scope(records(rows), cfg)
    iv = build_intervals(scope, UNITS, NO_MASKS, cfg)
    return AlertHistory(build_seen(scope, UNITS, cfg), iv, ['U_A', 'U_B'])


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


def test_invented_end_stays_open_until_next_alert(cfg):
    """A record of exactly 1 h may carry the processor's invented end, written only at the next start.

    Until then no all-clear had been seen, so the alert is open. The decision uses the record alone:
    whether the next alert comes after 2 h (a real end, retrospectively) or after 5 h (rule (b))
    is the future and must not change the answer at 12:00.
    """
    T = pd.DatetimeIndex([utc('2026-01-10T10:30:00Z'), utc('2026-01-10T12:00:00Z')])
    answers = []
    for next_start in ['2026-01-10T12:30:00Z', '2026-01-10T15:00:00Z']:
        nxt = utc(next_start)
        rows = [('B', 'Raion 3', 'raion', '2026-01-10T10:00:00Z', '2026-01-10T11:00:00Z'),  # exactly 1 h
                ('B', 'Raion 3', 'raion', nxt, nxt + 30 * pd.Timedelta(minutes=1))]
        h = history(rows, cfg)
        answers.append((h.active(T)[:, 1].tolist(), h.seconds_since_end(T)[:, 1].tolist(),
                        h.seconds_active(T, 3 * H)[:, 1].tolist()))
        # once the next alert has started, the unit is under alert without a gap
        assert h.active(pd.DatetimeIndex([nxt - pd.Timedelta(seconds=1), nxt]))[:, 1].tolist() == [True, True]
    np.testing.assert_equal(answers[0], answers[1])        # NaN-aware comparison
    active, since_end, seconds = answers[0]
    assert active == [True, True]
    assert np.isnan(since_end).all()                       # no end has been seen yet
    assert seconds == [30 * 60, 120 * 60]


def test_alert_without_all_clear_stops_counting_after_cap(cfg):
    """D19: one record open for 30 h counts as active for 24 h only; a unit made of several raions
    whose overlapping records chain for 40 h stays active all along (the cap is per record)."""
    rows = [('B', 'Raion 3', 'raion', '2026-01-10T00:00:00Z', '2026-01-11T06:00:00Z')]   # 30 h, one record
    t0 = utc('2026-01-10T00:00:00Z')
    for k in range(5):                                                                   # U_A: 5 x 10 h, overlapping
        ra = 'Raion 1' if k % 2 == 0 else 'Raion 2'
        rows.append(('A', ra, 'raion', t0 + k * 8 * H, t0 + k * 8 * H + 10 * H))
    h = history(rows, cfg)
    T = pd.DatetimeIndex([t0 + 23 * H, t0 + 25 * H, t0 + 39 * H])
    assert h.active(T)[:, 1].tolist() == [True, False, False]
    assert h.active(T)[:, 0].tolist() == [True, True, True]


def test_corrupting_the_future_changes_nothing(cfg):
    """Rebuild intervals after replacing every timestamp later than t with noise: answers at <= t stay."""
    rng = np.random.default_rng(0)
    t0, locs = utc('2026-01-05T00:00:00Z'), [('A', 'Raion 1'), ('A', 'Raion 2'), ('B', 'Raion 3')]
    rows = []
    for _ in range(400):
        ob, ra = locs[rng.integers(3)]
        s = t0 + pd.Timedelta(seconds=int(rng.integers(0, 20 * 86400)))
        # every fifth record has the processor's invented length of exactly 1 h
        length = 3600 if rng.random() < 0.2 else int(rng.integers(60, 4 * 3600))
        rows.append((ob, ra, 'raion', s, s + pd.Timedelta(seconds=length)))
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
