"""D22: the period of the alerts.in.ua source comes from what was downloaded, oblast by oblast."""
import pandas as pd
import pytest
from conftest import utc

from alerts.api_check import api_config
from alerts.ingest.alerts_in_ua import downloads

SUNDAY = utc('2026-10-11T08:45:00Z')
MONDAY = utc('2026-10-12T14:10:00Z')


def batch(uids, at):
    """One download pass: a request per uid, 31 s apart."""
    return pd.DataFrame({'uid': [str(u) for u in uids],
                         'requested_utc': [at + pd.Timedelta(seconds=31 * i) for i in range(len(uids))]})


def config(cfg, d):
    cfg['api'] = {'oblast_uids': [3, 4, 5]}
    c = api_config(cfg, d)
    return c['periods']['work_start'][:16], c['data_end'][:16]


def test_one_download(cfg):
    assert config(cfg, batch([3, 4, 5], SUNDAY)) == ('2026-09-12T00:00', '2026-10-11T08:00')


def test_second_download_extends_both_ends(cfg):
    """The Monday pass adds Monday; the start stays where the Sunday responses begin."""
    d = pd.concat([batch([3, 4, 5], SUNDAY), batch([3, 4, 5], MONDAY)])
    assert config(cfg, d) == ('2026-09-12T00:00', '2026-10-12T14:00')


def test_interrupted_download_keeps_the_old_end(cfg):
    """uid 5 was not downloaded again: after Sunday its oblast is unknown, not quiet."""
    d = pd.concat([batch([3, 4, 5], SUNDAY), batch([3, 4], MONDAY)])
    assert config(cfg, d)[1] == '2026-10-11T08:00'


def test_other_uids_do_not_count_and_missing_oblasts_fail(cfg):
    d = pd.concat([batch([3, 4, 5], SUNDAY), batch([999], utc('2026-10-01T00:00:00Z'))])
    assert config(cfg, d) == ('2026-09-12T00:00', '2026-10-11T08:00')
    with pytest.raises(ValueError, match='5'):
        config(cfg, batch([3, 4], SUNDAY))


def test_downloads_reads_file_names(tmp_path):
    for name in ['22_20261011T084539Z.json', '3_20261011T084610Z.json', '3_20261012T141000Z.json']:
        (tmp_path / name).write_text('{"alerts": []}', encoding='utf-8')
    (tmp_path / 'manifest.jsonl').write_text('', encoding='utf-8')
    d = downloads(tmp_path).sort_values(['uid', 'requested_utc']).reset_index(drop=True)
    assert d['uid'].tolist() == ['22', '3', '3']
    assert d['requested_utc'].tolist() == [utc('2026-10-11T08:45:39Z'), utc('2026-10-11T08:46:10Z'), MONDAY]
