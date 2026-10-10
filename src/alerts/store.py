"""Reading and writing pipeline tables with explicit types (CSV keeps them diffable in git)."""
import pandas as pd

from alerts.config import path
from alerts.intervals import INTERVAL_COLUMNS
from alerts.mask import MASK_COLUMNS

UNIT_COLUMNS = ['oblast', 'raion', 'unit_id', 'unit_name', 'role']


def _utc(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, utc=True).dt.as_unit('s')


def save(df: pd.DataFrame, cfg: dict, key: str) -> None:
    p = path(cfg, key)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False)


def load_units(cfg: dict) -> pd.DataFrame:
    return pd.read_csv(path(cfg, 'units'))[UNIT_COLUMNS]


def load_masks(cfg: dict) -> pd.DataFrame:
    m = pd.read_csv(path(cfg, 'mask'))[MASK_COLUMNS]
    return m.assign(start=_utc(m['start']), end=_utc(m['end']))


def load_intervals(cfg: dict) -> pd.DataFrame:
    iv = pd.read_csv(path(cfg, 'intervals'))[INTERVAL_COLUMNS]
    return iv.assign(start_utc=_utc(iv['start_utc']), end_utc=_utc(iv['end_utc']),
                     open_until=_utc(iv['open_until']),
                     uncertain=iv['uncertain'].astype(bool))
