import copy

import pandas as pd
import pytest

_BASE_CFG = {
    'dataset': {'repo_url': '', 'commit': '', 'repo_dir': '', 'path': '', 'sha256': ''},
    'data_end': '2026-03-01T00:00:00Z',
    'periods': {'work_start': '2026-01-01T00:00:00Z', 'warmup_end': '2026-01-02T00:00:00Z',
                'train_end': '2026-02-01T00:00:00Z', 'val_end': '2026-02-15T00:00:00Z'},
    'scope': {'excluded_oblasts': [], 'input_only_oblasts': [], 'oblast_level_units': []},
    # Synthetic data is sparse: the outage rule is switched off unless a test turns it on.
    'thresholds': {'pause_merge_min': 15, 'long_alert_hours': 24, 'clone_jaccard': 0.997,
                   'similar_pairs_report': 0.95, 'outage_gap_hours': 1_000_000},
    'processor': {'fake_end_duration_s': 3600, 'fake_end_next_start_h': 3},
    'horizons': [1, 3, 6],
    'paths': {'units': '', 'mask': '', 'intervals': '', 'similar_pairs': '', 'reports': ''},
}


@pytest.fixture
def cfg():
    return copy.deepcopy(_BASE_CFG)


def records(rows) -> pd.DataFrame:
    """Source records in the loader's format from (oblast, raion | None, level, start, end) tuples."""
    df = pd.DataFrame(rows, columns=['oblast', 'raion', 'level', 'started_at', 'finished_at'])
    for c in ['started_at', 'finished_at']:
        df[c] = pd.to_datetime(df[c], utc=True).dt.as_unit('s')
    df['duration'] = (df['finished_at'] - df['started_at']).dt.total_seconds()
    return df


def units_table(rows) -> pd.DataFrame:
    """Units table from (oblast, raion, unit_id) tuples; all target."""
    u = pd.DataFrame(rows, columns=['oblast', 'raion', 'unit_id'])
    return u.assign(unit_name=u['raion'], role='target')


def utc(s: str) -> pd.Timestamp:
    return pd.Timestamp(s).tz_convert('UTC').as_unit('s')
