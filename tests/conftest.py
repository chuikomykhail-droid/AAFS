import copy

import pandas as pd
import pytest

_BASE_CFG = {
    'dataset': {'repo_url': '', 'commit': '', 'repo_dir': '', 'path': '', 'sha256': '', 'path_uk': '', 'sha256_uk': ''},
    'volunteer': {'commit': '', 'path': '', 'sha256': ''},
    'data_end': '2026-03-01T00:00:00Z',
    'periods': {'work_start': '2026-01-01T00:00:00Z', 'warmup_end': '2026-01-02T00:00:00Z',
                'train_end': '2026-02-01T00:00:00Z', 'val_end': '2026-02-15T00:00:00Z'},
    'scope': {'excluded_oblasts': [], 'input_only_oblasts': [], 'oblast_level_units': []},
    # Synthetic data is sparse: the outage rule is switched off unless a test turns it on.
    'thresholds': {'pause_merge_min': 15, 'long_alert_hours': 24, 'clone_jaccard': 0.997,
                   'similar_pairs_report': 0.95, 'outage_gap_hours': 1_000_000},
    'processor': {'enabled': True, 'fake_end_duration_s': 3600, 'fake_end_next_start_h': 3},
    'history': {'max_open_hours': 24},
    'geo': {'path': '', 'sha256': '', 'vertex_decimals': 5, 'min_shared_vertices': 2, 'renames': {}},
    'backtest': {'horizons': [3], 'baselines': ['B0', 'B1', 'B2'], 'models': ['LR', 'LGBM']},
    'models': {'threads': 2, 'seed': 1,
               'lr': {'grid': {'C': [1.0], 'half_life_days': [None, 28]}},
               'lgbm': {'learning_rate': 0.1, 'max_estimators': 60, 'early_stopping_rounds': 10,
                        'grid': {'num_leaves': [7], 'min_child_samples': [20], 'half_life_days': [None, 28]}}},
    'baselines': {'b1_window_days': 28, 'prior_strength': 5},
    'bootstrap': {'n_reps': 50, 'n_reps_oblast': 20, 'ci': 0.95, 'seed': 1},
    'leakage_check': {'cuts': [], 'horizon': 3},
    'report': {'forecast_units': [], 'forecast_days': 7},
    'api': {'base_url': '', 'history_path': '', 'token_env': '', 'token_file': '', 'pause_seconds': 0,
            'retry_after_429_seconds': 0, 'raw_dir': '', 'oblast_uids': []},
    'levels': {'kyiv_start': '', 'lviv_start': '', 'channel_stop': '', 'horizon': 3},
    'visuals': {'map_decimals': 2, 'horizon': 3, 'gif_lead_hours': 12, 'gif_hours': 36, 'gif_frame_minutes': 15, 'gif_frame_ms': 120, 'forecast_min_train_days': 14},
    'horizons': [1, 3, 6],
    'paths': {'units': '', 'mask': '', 'intervals': '', 'seen': '', 'neighbors': '', 'grid': '', 'predictions': '', 'similar_pairs': '', 'reports': ''},
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
