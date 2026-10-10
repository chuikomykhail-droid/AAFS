"""Forecast scope (D05, D06): which source records feed which unit, over which period.

The only place where scope rules live; every stage gets its records from select_scope().
"""
import numpy as np
import pandas as pd

from alerts.config import ts

LEVEL_RAION = 'raion'
LEVEL_OBLAST = 'oblast'
ROLE_TARGET = 'target'
ROLE_INPUT = 'input'

LOC_KEY = ['oblast', 'raion']


def select_scope(df: pd.DataFrame, cfg: dict, period: bool = True) -> pd.DataFrame:
    """Source records in scope, one row per record.

    role='target': raion-level records outside excluded and input-only oblasts, plus
        oblast-level records of `oblast_level_units` (Kyiv, D05); for those, raion = oblast name.
    role='input': raion-level records of input-only oblasts (Donetsk, D06): features only.

    period=True keeps records that overlap [work_start, data_end) and does not clip them:
    clipping would invent an alert start at work_start. period=False is for rules that need
    neighbouring records outside the period (next start in mask rule (b)).
    """
    sc = cfg['scope']
    _check_oblast_names(df, sc)

    is_raion = df['level'] == LEVEL_RAION
    special = df['oblast'].isin(sc['oblast_level_units'])
    if (is_raion & special).any():
        raise ValueError('raion-level records appeared for an oblast-level unit; D05 needs revisiting')
    if df.loc[is_raion, 'raion'].isna().any():
        raise ValueError('raion-level records without a raion name')

    not_target = sc['excluded_oblasts'] + sc['input_only_oblasts']
    target = (is_raion & ~df['oblast'].isin(not_target)) | ((df['level'] == LEVEL_OBLAST) & special)
    inputs = is_raion & df['oblast'].isin(sc['input_only_oblasts'])

    cols = ['oblast', 'raion', 'level', 'started_at', 'finished_at', 'duration']
    out = df.loc[target | inputs, cols].copy()
    out['role'] = np.where(inputs[target | inputs], ROLE_INPUT, ROLE_TARGET)
    out['raion'] = out['raion'].fillna(out['oblast'])

    if period:
        work_start, data_end = ts(cfg['periods']['work_start']), ts(cfg['data_end'])
        out = out[(out['started_at'] < data_end) & (out['finished_at'] > work_start)]
    return out.reset_index(drop=True)


def attach_units(records: pd.DataFrame, units: pd.DataFrame) -> pd.DataFrame:
    """Add unit_id by the (oblast, raion) key. Every record must map: nothing is dropped silently."""
    out = records.merge(units[LOC_KEY + ['unit_id']], on=LOC_KEY, how='left', validate='many_to_one')
    unmapped = out.loc[out['unit_id'].isna(), LOC_KEY].drop_duplicates()
    if len(unmapped):
        raise ValueError(f'locations without a unit: {unmapped.to_dict("records")}')
    return out


def _check_oblast_names(df: pd.DataFrame, sc: dict) -> None:
    named = set(sc['excluded_oblasts']) | set(sc['input_only_oblasts']) | set(sc['oblast_level_units'])
    unknown = sorted(named - set(df['oblast'].dropna().unique()))
    if unknown:
        raise ValueError(f'oblasts from config.scope are not in the data: {unknown}')
