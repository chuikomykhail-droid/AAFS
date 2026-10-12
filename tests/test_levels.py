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
