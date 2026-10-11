"""PLAN stage 4: corrupt every record after a cut; forecasts at the cut must not change at all."""
import numpy as np
import pandas as pd
from conftest import records, units_table, utc

from alerts.leakage import check, corrupt_after
from alerts.models import registry

UNITS = units_table([('A', 'Raion 1', 'U_A'), ('A', 'Raion 2', 'U_A'), ('B', 'Raion 3', 'U_B'),
                     ('B', 'Raion 4', 'U_C'), ('C', 'Raion 5', 'U_D')])
LOCS = [('A', 'Raion 1'), ('A', 'Raion 2'), ('B', 'Raion 3'), ('B', 'Raion 4'), ('C', 'Raion 5')]
_PAIRS = [('unit', 'U_A', 'U_B'), ('unit', 'U_B', 'U_C'), ('unit', 'U_C', 'U_D'), ('oblast', 'A', 'B'), ('oblast', 'B', 'C')]
NEIGHBORS = pd.DataFrame([(lv, a, b) for lv, x, y in _PAIRS for a, b in [(x, y), (y, x)]], columns=['level', 'a', 'b'])


def synthetic(seed=0, n=2500):
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n):
        ob, ra = LOCS[rng.integers(len(LOCS))]
        s = utc('2026-01-01T00:00:00Z') + pd.Timedelta(seconds=int(rng.integers(0, 59 * 86400)))
        length = 3600 if rng.random() < 0.03 else int(rng.integers(120, 5 * 3600))
        rows.append((ob, ra, 'raion', s, s + pd.Timedelta(seconds=length)))
    return records(rows)


def test_corruption_changes_only_the_future():
    df = synthetic()
    cut = utc('2026-02-20T00:00:00Z')
    bad = corrupt_after(df, cut)
    past = df['finished_at'] <= cut
    pd.testing.assert_frame_equal(df[past].reset_index(drop=True), bad[past.to_numpy()].reset_index(drop=True))
    assert not df[~past].reset_index(drop=True).equals(bad[~past.to_numpy()].reset_index(drop=True))


PARAMS = {'LR': {'C': 1.0, 'half_life_days': 28},
          'LGBM': {'num_leaves': 7, 'min_child_samples': 20, 'half_life_days': 28, 'n_estimators': 40}}


def test_forecasts_at_the_cut_do_not_change(cfg):
    df = synthetic()
    models = registry(cfg, cfg['backtest']['baselines'] + cfg['backtest']['models'], PARAMS)
    for cut in ['2026-02-16T00:00:00Z', '2026-02-20T13:00:00Z']:
        for h in [1, 3]:
            res = check(df, cfg, utc(cut), h, models, units=UNITS, neighbors=NEIGHBORS)
            assert res['future_changed'] and res['rows_at_cut'] > 0 and res['training_rows'] > 1000
