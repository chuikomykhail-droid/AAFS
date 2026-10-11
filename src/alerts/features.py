"""Features for every grid row, computed as of t and vectorised over all moments (PLAN stage 5; D16, D19).

Every feature reads alert history only through AlertHistory, so it uses events with timestamp <= t.
The state of a unit "now" comes from the seen table (no bridged pauses, invented ends kept open,
alerts without an all-clear dropped after history.max_open_hours). Oblast and country features
include the input-only unit of Donetsk oblast (D06). Neighbours come from the raion boundaries (geo).

Channel outages (D15): counts over 7 days are scaled to the observed part of the window, the time
since the last end counts observed time only, and rows whose last 24 hours overlap an outage are
not usable (`lookback_ok` is False): their 6- and 24-hour windows are incomplete.
"""
import numpy as np
import pandas as pd

from alerts.history import AlertHistory
from alerts.timeutil import to_sec

KYIV = 'Europe/Kyiv'
HOUR = pd.Timedelta(hours=1)
MINUTE = pd.Timedelta(minutes=1)

GROUPS = {
    'own': ['since_end_log_h', 'starts_6h', 'starts_24h', 'starts_7d', 'active_share_24h'],
    'oblast': ['oblast_active_share', 'oblast_starts_30m', 'oblast_starts_60m'],
    'country': ['oblasts_active', 'country_starts_30m', 'country_starts_60m'],
    'neighbours': ['neighbor_oblasts_active_share', 'neighbor_units_active_share', 'neighbor_starts_60m'],
    'calendar': ['hour_kyiv', 'dow_kyiv', 'hour_sin', 'hour_cos', 'dow_sin', 'dow_cos'],
}
NUMERIC = [f for g in GROUPS.values() for f in g]


class FeatureBuilder:
    def __init__(self, seen: pd.DataFrame, intervals: pd.DataFrame, units: pd.DataFrame,
                 masks: pd.DataFrame, neighbors: pd.DataFrame, cfg: dict):
        self.cfg = cfg
        u = units.drop_duplicates('unit_id')
        self.unit_ids = u['unit_id'].tolist()                    # target and input units
        self.col = {uid: j for j, uid in enumerate(self.unit_ids)}
        self.oblasts = sorted(u['oblast'].unique())
        ob_idx = {ob: i for i, ob in enumerate(self.oblasts)}
        self.unit_oblast = u['oblast'].map(ob_idx).to_numpy()
        self.OB = np.zeros((len(self.unit_ids), len(self.oblasts)))
        self.OB[np.arange(len(self.unit_ids)), self.unit_oblast] = 1

        nu = neighbors[neighbors['level'] == 'unit']
        self.A = np.zeros((len(self.unit_ids), len(self.unit_ids)))
        self.A[nu['a'].map(self.col).to_numpy(), nu['b'].map(self.col).to_numpy()] = 1
        no = neighbors[neighbors['level'] == 'oblast']
        self.O = np.zeros((len(self.oblasts), len(self.oblasts)))
        self.O[no['a'].map(ob_idx).to_numpy(), no['b'].map(ob_idx).to_numpy()] = 1
        if (self.A.sum(axis=1) == 0).any() or (self.O.sum(axis=1) == 0).any():
            raise ValueError('a unit or an oblast without neighbours')

        self.history = AlertHistory(seen, intervals, self.unit_ids, masks)

    def build(self, grid: pd.DataFrame) -> pd.DataFrame:
        """Features per grid row (same index), plus `lookback_ok`. The grid needs columns unit_id and t."""
        T = pd.DatetimeIndex(np.sort(grid['t'].unique()))
        t = to_sec(T)
        ti = np.searchsorted(t, to_sec(grid['t']))
        uj = grid['unit_id'].map(self.col)
        if uj.isna().any():
            raise ValueError('grid has units unknown to the feature builder')
        uj = uj.to_numpy(dtype=int)
        oj = self.unit_oblast[uj]
        h = self.history

        act = h.active(T).astype(float)                                   # (moments, units)
        starts = {w: h.starts(T, w).astype(float)
                  for w in [30 * MINUTE, 60 * MINUTE, 6 * HOUR, 24 * HOUR, 7 * 24 * HOUR]}
        out24 = h.outage_seconds(T, 24 * HOUR)
        out7d = h.outage_seconds(T, 7 * 24 * HOUR)
        week = 7 * 24 * 3600.0

        since = h.seconds_since_end(T)                                    # NaN: no end seen yet
        last_end = np.where(np.isnan(since), t[:, None], t[:, None] - np.nan_to_num(since))
        since_obs = since - h.outage_between(last_end.ravel().astype(np.int64),
                                             np.repeat(t, since.shape[1])).reshape(since.shape)

        obl_active = act @ self.OB                                        # units under alert per oblast
        obl_any = (obl_active > 0).astype(float)
        obl_n = self.OB.sum(axis=0)

        f = pd.DataFrame(index=grid.index)
        f['since_end_log_h'] = np.log1p(since_obs[ti, uj] / 3600)
        f['starts_6h'] = starts[6 * HOUR][ti, uj]
        f['starts_24h'] = starts[24 * HOUR][ti, uj]
        f['starts_7d'] = starts[7 * 24 * HOUR][ti, uj] * (week / (week - out7d))[ti]
        f['active_share_24h'] = h.seconds_active(T, 24 * HOUR)[ti, uj] / (24 * 3600)

        others = obl_n[oj] - 1
        f['oblast_active_share'] = np.where(others > 0, (obl_active[ti, oj] - act[ti, uj]) / np.maximum(others, 1),
                                            np.nan)
        f['oblast_starts_30m'] = (starts[30 * MINUTE] @ self.OB)[ti, oj]
        f['oblast_starts_60m'] = (starts[60 * MINUTE] @ self.OB)[ti, oj]

        f['oblasts_active'] = obl_any.sum(axis=1)[ti]
        f['country_starts_30m'] = starts[30 * MINUTE].sum(axis=1)[ti]
        f['country_starts_60m'] = starts[60 * MINUTE].sum(axis=1)[ti]

        f['neighbor_oblasts_active_share'] = ((obl_any @ self.O.T) / self.O.sum(axis=1))[ti, oj]
        f['neighbor_units_active_share'] = ((act @ self.A.T) / self.A.sum(axis=1))[ti, uj]
        f['neighbor_starts_60m'] = (starts[60 * MINUTE] @ self.A.T)[ti, uj]

        kyiv = grid['t'].dt.tz_convert(KYIV)
        f['hour_kyiv'] = kyiv.dt.hour.to_numpy()
        f['dow_kyiv'] = kyiv.dt.dayofweek.to_numpy()
        f['hour_sin'] = np.sin(2 * np.pi * f['hour_kyiv'] / 24)
        f['hour_cos'] = np.cos(2 * np.pi * f['hour_kyiv'] / 24)
        f['dow_sin'] = np.sin(2 * np.pi * f['dow_kyiv'] / 7)
        f['dow_cos'] = np.cos(2 * np.pi * f['dow_kyiv'] / 7)

        f = f[NUMERIC].astype('float32')
        f['lookback_ok'] = out24[ti] == 0
        return f
