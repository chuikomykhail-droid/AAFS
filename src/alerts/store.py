"""Reading and writing pipeline tables with explicit types (CSV keeps them diffable in git)."""
import pandas as pd

from alerts.config import path
from alerts.intervals import INTERVAL_COLUMNS, SEEN_COLUMNS
from alerts.mask import MASK_COLUMNS

UNIT_COLUMNS = ['oblast', 'raion', 'unit_id', 'unit_name', 'role']


def _utc(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, utc=True).dt.as_unit('s')


def save(df: pd.DataFrame, cfg: dict, key: str) -> None:
    p = path(cfg, key)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False)


def save_parquet(df: pd.DataFrame, cfg: dict, key: str) -> None:
    """Large derived tables: parquet keeps types and stays small; they are not tracked in git."""
    p = path(cfg, key)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(p, index=False)


def load_grid(cfg: dict) -> pd.DataFrame:
    return pd.read_parquet(path(cfg, 'grid'))


def load_seen(cfg: dict) -> pd.DataFrame:
    s = pd.read_csv(path(cfg, 'seen'))[SEEN_COLUMNS]
    return s.assign(start=_utc(s['start']), end=_utc(s['end']))


def load_units(cfg: dict) -> pd.DataFrame:
    return pd.read_csv(path(cfg, 'units'))[UNIT_COLUMNS]


def load_masks(cfg: dict) -> pd.DataFrame:
    m = pd.read_csv(path(cfg, 'mask'))[MASK_COLUMNS]
    return m.assign(start=_utc(m['start']), end=_utc(m['end']))


def load_intervals(cfg: dict) -> pd.DataFrame:
    iv = pd.read_csv(path(cfg, 'intervals'))[INTERVAL_COLUMNS]
    return iv.assign(start_utc=_utc(iv['start_utc']), end_utc=_utc(iv['end_utc']),
                     uncertain=iv['uncertain'].astype(bool))
