"""Loading config.yaml. Every threshold and date lives there, none in the code (PLAN 1б.6)."""
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]

_REQUIRED = {
    'dataset': ['repo_url', 'commit', 'repo_dir', 'path', 'sha256'],
    'periods': ['work_start', 'warmup_end', 'train_end', 'val_end'],
    'scope': ['excluded_oblasts', 'input_only_oblasts', 'oblast_level_units'],
    'thresholds': ['pause_merge_min', 'long_alert_hours', 'clone_jaccard',
                   'similar_pairs_report', 'outage_gap_hours'],
    'processor': ['fake_end_duration_s', 'fake_end_next_start_h'],
    'history': ['max_open_hours'],
    'geo': ['path', 'sha256', 'vertex_decimals', 'min_shared_vertices', 'renames'],
    'backtest': ['horizons', 'baselines', 'models'],
    'models': ['threads', 'seed', 'lr', 'lgbm'],
    'baselines': ['b1_window_days', 'prior_strength'],
    'bootstrap': ['n_reps', 'n_reps_oblast', 'ci', 'seed'],
    'leakage_check': ['cuts', 'horizon'],
    'paths': ['units', 'mask', 'intervals', 'seen', 'neighbors', 'grid', 'predictions', 'similar_pairs', 'reports'],
}


def load_config(path=None) -> dict:
    """Read the config and fail on any missing key: silent defaults hide typos."""
    path = Path(path) if path else ROOT / 'config.yaml'
    with open(path, encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    missing = [f'{sec}.{key}' for sec, keys in _REQUIRED.items() for key in keys
               if key not in (cfg.get(sec) or {})]
    missing += [key for key in ('data_end', 'horizons') if key not in cfg]
    if missing:
        raise KeyError(f'config is missing keys: {missing}')
    return cfg


def ts(value) -> pd.Timestamp:
    """Config timestamp as tz-aware UTC with second resolution."""
    return pd.Timestamp(value).tz_convert('UTC').as_unit('s')


def path(cfg: dict, key: str) -> Path:
    """Output path from the config, resolved against the repository root (not the CWD)."""
    return ROOT / cfg['paths'][key]
