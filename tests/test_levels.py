"""D23: level of the first alert in the window, and the before / after split."""
import pandas as pd
from conftest import utc

from alerts.levels import first_level, split_parts
from alerts.timeutil import to_sec


def rec_levels(rows):
    """(unit_id, start, level) tuples -> the frame of levels.record_levels."""
    d = pd.DataFrame(rows, columns=['unit_id', 'start', 'level'])
    return d.assign(start=to_sec(pd.to_datetime(d['start'], utc=True)))


def test_first_level_takes_the_first_start_after_t():
    lv = rec_levels([('U1', '2026-10-01T10:30:00Z', 'yellow'), ('U1', '2026-10-01T11:30:00Z', 'red'),
                     ('U2', '2026-10-01T12:00:00Z', 'red'), ('U2', '2026-10-01T12:00:00Z', 'yellow')])
    rows = pd.DataFrame({'unit_id': ['U1', 'U1', 'U1', 'U2', 'U2'],
                         't': [utc('2026-10-01T10:00:00Z'), utc('2026-10-01T10:30:00Z'), utc('2026-10-01T12:00:00Z'),
                               utc('2026-10-01T09:00:00Z'), utc('2026-10-01T08:00:00Z')]})
    got = first_level(rows, lv, h=3).tolist()
    # a start exactly at t is not in (t, t+h]; a start exactly at t+h is; clones starting together -> both
    assert got == ['yellow', 'red', None, 'both', None]


def test_split_parts():
    p = pd.DataFrame({'oblast': ['A', 'A', 'B', 'C'],
                      't': [utc('2026-09-01T00:00:00Z'), utc('2026-09-10T00:00:00Z'),
                            utc('2026-09-10T00:00:00Z'), utc('2026-09-10T00:00:00Z')]})
    part = split_parts(p, {'A': utc('2026-09-10T00:00:00Z'), 'B': pd.NaT})
    assert part.iloc[:3].tolist() == ['before', 'after', 'before']
    assert pd.isna(part.iloc[3])


def test_area_coverage_is_time_weighted_over_minutes_with_an_alert():
    from alerts.levels import area_coverage, minute_series
    raions = pd.DataFrame({'oblast': ['A', 'A', 'B'], 'raion': ['a1', 'a2', 'b1'], 'area': [3.0, 1.0, 5.0]})
    rec = pd.DataFrame({'oblast': ['A', 'A'], 'raion': ['a1', 'a2'],
                        'started_at': [utc('2026-10-01T00:00:00Z'), utc('2026-10-01T00:30:00Z')],
                        'finished_at': [utc('2026-10-01T01:00:00Z'), utc('2026-10-01T01:30:00Z')]})
    s = minute_series(rec, raions, utc('2026-10-01T00:00:00Z'), utc('2026-10-01T02:00:00Z'))
    assert s.sum(axis=1).tolist() == [60, 60, 0]
    c = area_coverage(s, raions)
    # oblast A: 30 min only a1 (3/4), 30 min both (1), 30 min only a2 (1/4); 90 minutes with an alert
    assert c.at['A', 'minutes'] == 90
    assert abs(c.at['A', 'area_share'] - (0.75 + 1 + 0.25) / 3) < 1e-12
    assert c.at['B', 'minutes'] == 0 and pd.isna(c.at['B', 'area_share'])
