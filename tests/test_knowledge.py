"""D21: every feature must use only what the dataset contained at t, including records written late."""
import pandas as pd
from conftest import records, utc
from test_leakage import NEIGHBORS, UNITS, synthetic

from alerts.leakage import knowledge_check, known_at

CUT = utc('2026-02-20T12:00:00Z')


def with_invented_end(seed=0):
    """Random data plus, on Raion 5, a record of exactly 1 h whose invented end is written after the cut."""
    df = synthetic(seed)
    quiet = (df['raion'] == 'Raion 5') & (df['started_at'] > CUT - pd.Timedelta(days=2))
    extra = records([('C', 'Raion 5', 'raion', CUT - pd.Timedelta(hours=5), CUT - pd.Timedelta(hours=4)),
                     ('C', 'Raion 5', 'raion', CUT + pd.Timedelta(hours=2), CUT + pd.Timedelta(hours=3))])
    return pd.concat([df[~quiet], extra], ignore_index=True)


def test_known_at_replays_the_writing_of_records(cfg):
    df = with_invented_end()
    known = known_at(df, CUT, cfg)
    assert (known['started_at'] <= CUT).all()
    r5 = known[(known['raion'] == 'Raion 5') & (known['started_at'] == CUT - pd.Timedelta(hours=5))]
    assert r5['finished_at'].tolist() == [CUT + pd.Timedelta(seconds=1)]     # still open: written at CUT + 2 h
    done = df[(df['finished_at'] <= CUT) & (df['duration'] != 3600)]
    assert len(known.merge(done, on=['raion', 'started_at', 'finished_at'])) == len(done)


def test_features_use_only_what_was_known(cfg):
    for seed in [0, 1]:
        res = knowledge_check(with_invented_end(seed), cfg, CUT, units=UNITS, neighbors=NEIGHBORS)
        assert res['rows'] > 100 and res['open_at_cut'] >= 1
