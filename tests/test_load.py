import pytest

from alerts.config import ROOT, load_config
from alerts.ingest.vadimkin import load_official


def test_load_official():
    cfg = load_config()
    path = ROOT / cfg['dataset']['path']
    if not path.exists():
        pytest.skip('Dataset not found locally: run scripts/fetch_data.py')

    df = load_official(path, cfg['dataset']['sha256'])

    assert df.attrs['row_counts'] == {'raw': 299_275, 'dedup': 185_430, 'cleaned': 185_428}
    assert len(df) == len(df.drop_duplicates()), 'Dataframe contains duplicates'
    for col in ['started_at', 'finished_at']:
        assert str(df[col].dt.tz) == 'UTC', f'{col} is not tz-aware UTC'
    assert (df['finished_at'] > df['started_at']).all(), 'Found duration <= 0'
