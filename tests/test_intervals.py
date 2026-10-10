import pandas as pd
import pytest
from conftest import records, units_table, utc

from alerts.intervals import build_intervals, episodes
from alerts.mask import MASK_COLUMNS
from alerts.scope import select_scope

NO_MASKS = pd.DataFrame(columns=MASK_COLUMNS)

UNITS = units_table([
    ('Kyiv City', 'Kyiv City', 'U_KYIV'),
    ('A', 'Raion 1', 'U_A'),
    ('A', 'Raion 2', 'U_A'),  # clone of Raion 1
    ('B', 'Raion 3', 'U_B'),
])


def kyiv(start, end):
    return ('Kyiv City', None, 'oblast', start, end)


def build(rows, cfg, masks=NO_MASKS):
    return episodes(build_intervals(select_scope(records(rows), cfg), UNITS, masks, cfg))


@pytest.fixture
def kyiv_cfg(cfg):
    cfg['scope']['oblast_level_units'] = ['Kyiv City']
    return cfg


def test_overlap_nesting_pauses_and_masks(kyiv_cfg):
    cfg = kyiv_cfg
    rows = [
        kyiv('2026-01-01T10:00:00Z', '2026-01-01T11:00:00Z'),  # overlap
        kyiv('2026-01-01T10:30:00Z', '2026-01-01T11:30:00Z'),
        kyiv('2026-01-02T10:00:00Z', '2026-01-02T12:00:00Z'),  # nested
        kyiv('2026-01-02T10:30:00Z', '2026-01-02T11:30:00Z'),
        kyiv('2026-01-03T10:00:00Z', '2026-01-03T11:00:00Z'),  # pause of exactly 15 min: merged
        kyiv('2026-01-03T11:15:00Z', '2026-01-03T12:00:00Z'),
        kyiv('2026-01-04T10:00:00Z', '2026-01-04T11:00:00Z'),  # pause of 16 min: not merged
        kyiv('2026-01-04T11:16:00Z', '2026-01-04T12:00:00Z'),
        ('B', 'Raion 3', 'raion', '2026-01-05T10:00:00Z', '2026-01-05T11:00:00Z'),
    ]
    masks = pd.DataFrame([{'unit_id': 'U_KYIV', 'start': utc('2026-01-04T10:00:00Z'),
                           'end': utc('2026-01-04T11:16:00Z'), 'reason': 'fake_1h'}])
    ep = build(rows, cfg, masks)
    k = ep[ep['unit_id'] == 'U_KYIV']
    k = k.set_index(k['start_utc'].dt.day.rename('day'))

    assert (k.loc[1, 'start_utc'], k.loc[1, 'end_utc']) == (utc('2026-01-01T10:00:00Z'), utc('2026-01-01T11:30:00Z'))
    assert (k.loc[2, 'start_utc'], k.loc[2, 'end_utc']) == (utc('2026-01-02T10:00:00Z'), utc('2026-01-02T12:00:00Z'))
    assert (k.loc[3, 'start_utc'], k.loc[3, 'end_utc']) == (utc('2026-01-03T10:00:00Z'), utc('2026-01-03T12:00:00Z'))
    jan4 = k.loc[4].sort_values('start_utc')
    assert len(jan4) == 2
    assert jan4['uncertain'].tolist() == [True, False]  # the mask ends where the second alert starts
    assert ep.loc[ep['unit_id'] == 'U_B', 'uncertain'].tolist() == [False]


def test_clones_seconds_apart_with_different_ends(cfg):
    """Clones from one post start seconds apart and end at slightly different moments."""
    rows = [
        ('A', 'Raion 1', 'raion', '2026-01-05T10:00:00Z', '2026-01-05T11:00:02Z'),
        ('A', 'Raion 2', 'raion', '2026-01-05T10:00:03Z', '2026-01-05T11:00:00Z'),
        # Raion 2 alone, 10 min after the union ends: one unit, so the pause is bridged
        ('A', 'Raion 2', 'raion', '2026-01-05T11:10:02Z', '2026-01-05T11:30:00Z'),
    ]
    iv = build_intervals(select_scope(records(rows), cfg), UNITS, NO_MASKS, cfg)
    assert len(iv) == 2                               # two segments ...
    assert iv['n_records'].tolist() == [2, 1]
    ep = episodes(iv)
    assert len(ep) == 1                               # ... one episode
    assert ep.loc[0, 'start_utc'] == utc('2026-01-05T10:00:00Z')
    assert ep.loc[0, 'end_utc'] == utc('2026-01-05T11:30:00Z')


def test_period_filter_keeps_crossing_records_unclipped(kyiv_cfg):
    cfg = kyiv_cfg
    rows = [
        kyiv('2025-12-31T10:00:00Z', '2025-12-31T11:00:00Z'),  # ends before work_start: dropped
        kyiv('2025-12-31T23:30:00Z', '2026-01-01T00:40:00Z'),  # crosses work_start: kept as is
        kyiv('2026-02-28T23:50:00Z', '2026-03-01T00:20:00Z'),  # crosses data_end: kept as is
        kyiv('2026-03-01T01:00:00Z', '2026-03-01T02:00:00Z'),  # starts after data_end: dropped
    ]
    ep = build(rows, cfg)
    assert ep['start_utc'].tolist() == [utc('2025-12-31T23:30:00Z'), utc('2026-02-28T23:50:00Z')]
    assert ep['end_utc'].tolist() == [utc('2026-01-01T00:40:00Z'), utc('2026-03-01T00:20:00Z')]


def test_unmapped_location_raises(cfg):
    rows = [('C', 'Unknown raion', 'raion', '2026-01-05T10:00:00Z', '2026-01-05T11:00:00Z')]
    with pytest.raises(ValueError, match='without a unit'):
        build(rows, cfg)


def test_unknown_oblast_in_config_raises(cfg):
    cfg['scope']['excluded_oblasts'] = ['Typo oblast']
    with pytest.raises(ValueError, match='not in the data'):
        build([kyiv('2026-01-01T10:00:00Z', '2026-01-01T11:00:00Z')], cfg)
