"""The forecast at one moment for every unit: the interface for embedding (a bot, a web service).
Computation only; scripts/forecast.py is the command line around it (and caches the model frame).

    fc = Forecaster(cfg, model_frame)            # model_frame = pipeline.model_data(build_all(cfg), cfg)
    res = fc.at('2026-08-27 01:00', h=3)         # Kyiv time unless utc=True
    res.table                                    # one row per target unit, most likely first
    res.to_dict()                                # the same as JSON-ready data

A replay without a look into the future:
  * source 'vadimkin': LightGBM (hyperparameters of D20) is fitted on the rows whose labels were known at
    the moment (t <= moment - h), like one step of the walk-forward backtest; B1 on the same rows;
  * source 'api': the models frozen on all Vadimkin rows (stage 8, D22), features from the downloaded
    alerts.in.ua month.
Features come from AlertHistory as of the moment (D16, D21). The moment is rounded down to the hour:
forecasts are made at the top of each hour. What happened in (t, t+h] is attached when the data have it.
This is not a live forecast: the data end on 7 September (Vadimkin) and on the day of the API download.
"""
import json
from dataclasses import dataclass

import numpy as np
import pandas as pd

from alerts import api_check as ac
from alerts import store
from alerts.config import ROOT, path, ts
from alerts.history import AlertHistory
from alerts.ingest.alerts_in_ua import build_locations, downloads, load_alerts_in_ua, read_raw
from alerts.intervals import episodes
from alerts.models.baselines import UnitHourRate
from alerts.models.learned import GBMModel
from alerts.pipeline import build_tables, model_data
from alerts.scope import ROLE_TARGET

KYIV = 'Europe/Kyiv'
QUIET, UNDER_ALERT, NO_FORECAST = 'quiet', 'under_alert', 'no_forecast'


def moment(text, utc: bool = False) -> pd.Timestamp:
    """A moment from text or a timestamp: Kyiv time unless utc (or tz-aware), rounded down to the hour."""
    t = pd.Timestamp(text)
    if t.tzinfo is None:
        t = t.tz_localize('UTC' if utc else KYIV, ambiguous=False, nonexistent='shift_forward')
    return t.tz_convert('UTC').floor('h').as_unit('s')


def short_name(name: str) -> str:
    parts = name.split(' + ')
    return parts[0] if len(parts) == 1 else f'{parts[0]} + {len(parts) - 1} more (one unit)'


@dataclass
class ForecastResult:
    moment: pd.Timestamp       # UTC, top of the hour
    h: int
    source: str
    model: str                 # how the model was fitted, in words
    outcome_known: bool        # does the data reach t + h
    table: pd.DataFrame        # unit_id, unit, oblast, status, p, p_b1, alert_started (UTC or NaT)

    @property
    def quiet(self) -> pd.DataFrame:
        return self.table[self.table['status'] == QUIET]

    def to_dict(self) -> dict:
        """JSON-ready: probabilities rounded to 4 digits, times in ISO 8601 UTC, nulls where undefined."""
        rows = []
        for r in self.table.itertuples():
            rows.append({'unit_id': r.unit_id, 'unit': r.unit, 'oblast': r.oblast, 'status': r.status,
                         'p': None if pd.isna(r.p) else round(float(r.p), 4),
                         'p_b1': None if pd.isna(r.p_b1) else round(float(r.p_b1), 4),
                         'alert_started_utc': None if pd.isna(r.alert_started) else r.alert_started.isoformat()})
        return {'moment_utc': self.moment.isoformat(), 'moment_kyiv': self.moment.tz_convert(KYIV).isoformat(),
                'horizon_h': self.h, 'question': f'will an air-raid alert start in the unit within {self.h} h',
                'source': self.source, 'model': f'LightGBM {self.model}', 'outcome_known': self.outcome_known,
                'units': rows}

    def to_json(self, **kw) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, **kw)


class Forecaster:
    """Everything needed to forecast any hour of one source. `model_frame`: the Vadimkin grid rows with
    features (pipeline.model_data); the models are always trained on it."""

    def __init__(self, cfg: dict, model_frame: pd.DataFrame, source: str = 'vadimkin', units: pd.DataFrame | None = None):
        if source not in ('vadimkin', 'api'):
            raise ValueError(f'unknown source {source!r}')
        self.cfg, self.train_frame, self.source = cfg, model_frame, source
        self.units = units if units is not None else store.load_units(cfg)
        self.names = self.units.drop_duplicates('unit_id').set_index('unit_id')
        self.targets = self.units.loc[self.units['role'] == ROLE_TARGET, 'unit_id'].drop_duplicates().tolist()
        self._frozen = {}
        if source == 'vadimkin':
            self.lo = ts(cfg['periods']['warmup_end']) + pd.Timedelta(days=cfg['visuals']['forecast_min_train_days'])
            self.hi = ts(cfg['data_end'])
            self.data = model_frame
            seen, intervals, masks = store.load_seen(cfg), store.load_intervals(cfg), store.load_masks(cfg)
        else:
            raw_dir = ROOT / cfg['api']['raw_dir']
            if not any(raw_dir.glob('*_*.json')):
                raise FileNotFoundError(f'no alerts.in.ua responses in {raw_dir}: run scripts/fetch_alerts_in_ua.py '
                                        'with your own token')
            run_cfg = ac.api_config(cfg, downloads(raw_dir))
            recs, _ = load_alerts_in_ua(read_raw(raw_dir), build_locations(self.units, cfg))
            art = build_tables(recs, run_cfg, units=self.units, neighbors=pd.read_csv(path(cfg, 'neighbors')))
            self.lo, self.hi = ts(run_cfg['periods']['warmup_end']), ts(run_cfg['data_end'])
            self.data = model_data(art, run_cfg)
            seen, intervals, masks = art.seen, art.intervals, art.masks
        self.history = AlertHistory(seen, intervals, self.names.index.tolist(), masks)
        self.episodes = episodes(intervals)

    def _models(self, t: pd.Timestamp, h: int):
        ycol = f'y_{h}'
        cut = t if self.source == 'vadimkin' else ts(self.cfg['data_end'])
        if self.source == 'api' and h in self._frozen:
            return self._frozen[h]
        f = self.train_frame
        train = f[(f['t'] <= cut - pd.Timedelta(hours=h)) & f[ycol].notna()]
        tuned = json.loads((path(self.cfg, 'reports') / f'tuning_h{h}.json').read_text(encoding='utf-8'))
        y = train[ycol].to_numpy(dtype=float)
        how = (f'fitted on the {len(train):,} rows whose labels were known at the moment (t <= moment - {h} h)'
               if self.source == 'vadimkin' else
               f'frozen: fitted once on all {len(train):,} Vadimkin rows up to 7 Sep (stage 8); features from the API')
        out = (GBMModel(self.cfg, tuned['LGBM']).fit(train, y), UnitHourRate(self.cfg).fit(train, y), how)
        if self.source == 'api':
            self._frozen[h] = out
        return out

    def at(self, when, h: int = 3, utc: bool = False) -> ForecastResult:
        t = moment(when, utc)
        if h not in self.cfg['horizons']:
            raise ValueError(f'h must be one of {self.cfg["horizons"]}')
        if not self.lo <= t < self.hi:
            raise ValueError(f'the moment must be in [{self.lo.tz_convert(KYIV):%Y-%m-%d %H:%M}, '
                             f'{self.hi.tz_convert(KYIV):%Y-%m-%d %H:%M}) Kyiv time for the {self.source} source')
        rows = self.data[self.data['t'] == t]
        gbm, b1, how = self._models(t, h)

        tab = pd.DataFrame({'unit_id': self.targets})
        under = dict(zip(self.names.index, self.history.active(pd.DatetimeIndex([t]))[0]))
        tab['status'] = [UNDER_ALERT if under[u] else NO_FORECAST for u in tab['unit_id']]
        tab['p'], tab['p_b1'] = np.nan, np.nan
        if len(rows):
            pos = tab.set_index('unit_id').index.get_indexer(rows['unit_id'])
            tab.loc[pos, 'p'] = gbm.predict_proba(rows)
            tab.loc[pos, 'p_b1'] = b1.predict_proba(rows)
            tab.loc[pos, 'status'] = QUIET
        ep = self.episodes
        win = ep[(ep['start_utc'] > t) & (ep['start_utc'] <= t + pd.Timedelta(hours=h))]
        tab['alert_started'] = tab['unit_id'].map(win.groupby('unit_id')['start_utc'].min())
        tab['unit'] = tab['unit_id'].map(self.names['unit_name']).map(short_name)
        tab['oblast'] = tab['unit_id'].map(self.names['oblast']).str.replace(' oblast', '')
        order = {QUIET: 0, UNDER_ALERT: 1, NO_FORECAST: 2}
        tab = (tab.assign(_o=tab['status'].map(order), _p=-tab['p'].fillna(-1))
                  .sort_values(['_o', '_p', 'unit']).drop(columns=['_o', '_p']).reset_index(drop=True))
        cols = ['unit_id', 'unit', 'oblast', 'status', 'p', 'p_b1', 'alert_started']
        return ForecastResult(t, h, self.source, how, t + pd.Timedelta(hours=h) <= self.hi, tab[cols])
