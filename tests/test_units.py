from conftest import records

from alerts.scope import select_scope
from alerts.units import build_units


def test_clones_merge_and_silent_pairs_do_not(cfg):
    """Identical train series merge (D07); two raions with no train alerts must not (union = 0)."""
    rows = []
    for day in range(2, 30):
        s, e = f'2026-01-{day:02d}T10:00:00Z', f'2026-01-{day:02d}T11:00:00Z'
        rows += [('A', 'Raion 1', 'raion', s, e), ('A', 'Raion 2', 'raion', s, e)]
        if day % 3 == 0:
            rows.append(('A', 'Raion 3', 'raion', s, e))
    # Raions 4 and 5 are silent on the train period and alert only in the test period
    rows += [('A', 'Raion 4', 'raion', '2026-02-20T10:00:00Z', '2026-02-20T11:00:00Z'),
             ('A', 'Raion 5', 'raion', '2026-02-21T10:00:00Z', '2026-02-21T11:00:00Z')]

    units, pairs = build_units(select_scope(records(rows), cfg), cfg)
    uid = units.set_index('raion')['unit_id']
    assert uid['Raion 1'] == uid['Raion 2'] == 'U000'
    assert units['unit_id'].nunique() == 4
    silent = pairs[(pairs['raion1'] == 'Raion 4') & (pairs['raion2'] == 'Raion 5')]['jaccard']
    assert silent.tolist() == [0.0]
