"""Baselines of PLAN stage 4 (D18). Same interface as the models: fit(X, y) / predict_proba(X).

X is the backtest frame: grid columns (unit_id, t, oblast, ...) plus features. Every rate is
shrunk towards its parent rate with additive smoothing of a fixed strength (config
baselines.prior_strength), so that cells with few rows do not produce 0 or 1.
"""
import numpy as np
import pandas as pd


def _smoothed(pos: pd.Series, n: pd.Series, parent, prior: float) -> pd.Series:
    return (pos + prior * parent) / (n + prior)


class GlobalRate:
    """B0: overall frequency of the target over the training rows."""
    name = 'B0'

    def __init__(self, cfg: dict):
        pass

    def fit(self, X: pd.DataFrame, y: np.ndarray):
        self.p_ = float(np.mean(y))
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return np.full(len(X), self.p_)


class UnitHourRate:
    """B1: frequency for unit x hour of day (Kyiv) over the last window_days of training rows.

    The window ends at the last training moment, which the backtest sets to (forecast day - h):
    the most recent rows whose labels are fully known.
    """
    name = 'B1'

    def __init__(self, cfg: dict):
        self.window = pd.Timedelta(days=cfg['baselines']['b1_window_days'])
        self.prior = cfg['baselines']['prior_strength']

    def fit(self, X: pd.DataFrame, y: np.ndarray):
        recent = (X['t'] > X['t'].max() - self.window).to_numpy()
        d = pd.DataFrame({'unit_id': X['unit_id'].to_numpy()[recent],
                          'hour': X['hour_kyiv'].to_numpy().astype(int)[recent], 'y': y[recent]})
        self.global_ = float(d['y'].mean())
        unit = d.groupby('unit_id')['y'].agg(['sum', 'count'])
        self.unit_ = _smoothed(unit['sum'], unit['count'], self.global_, self.prior)
        cell = d.groupby(['unit_id', 'hour'])['y'].agg(['sum', 'count'])
        parent = self.unit_.reindex(cell.index.get_level_values('unit_id')).to_numpy()
        self.cell_ = _smoothed(cell['sum'], cell['count'], parent, self.prior)
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        key = pd.MultiIndex.from_arrays([X['unit_id'].to_numpy(), X['hour_kyiv'].to_numpy().astype(int)])
        p = self.cell_.reindex(key).to_numpy()
        unit = self.unit_.reindex(X['unit_id'].to_numpy()).to_numpy()
        p = np.where(np.isnan(p), unit, p)
        return np.where(np.isnan(p), self.global_, p)


class WaveRate:
    """B2: frequency as a function of the number of oblasts under alert at t (the "wave")."""
    name = 'B2'

    def __init__(self, cfg: dict):
        self.prior = cfg['baselines']['prior_strength']

    def fit(self, X: pd.DataFrame, y: np.ndarray):
        d = pd.DataFrame({'k': X['oblasts_active'].to_numpy().astype(int), 'y': y})
        self.global_ = float(d['y'].mean())
        by_k = d.groupby('k')['y'].agg(['sum', 'count'])
        self.rate_ = _smoothed(by_k['sum'], by_k['count'], self.global_, self.prior)
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        p = self.rate_.reindex(X['oblasts_active'].to_numpy().astype(int)).to_numpy()
        return np.where(np.isnan(p), self.global_, p)


BASELINES = {m.name: m for m in [GlobalRate, UnitHourRate, WaveRate]}
