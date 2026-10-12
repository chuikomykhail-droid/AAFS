"""Stage 8: frozen models on fresh alerts.in.ua data (PLAN stage 8, D22). Computation only.

The two sources are never joined (D02): models are fitted once on Vadimkin rows and then only
predict; features on the API period are computed from API data alone, through the same AlertHistory.
"""
import copy
import hashlib
import io
import subprocess

import numpy as np
import pandas as pd

from alerts.config import ROOT
from alerts.intervals import episodes
from alerts.metrics import bootstrap
from alerts.scope import ROLE_TARGET
from alerts.spans import union
from alerts.timeutil import to_sec

KYIV = 'Europe/Kyiv'


# --- source profile (8.3) ------------------------------------------------------------------
def api_config(cfg: dict, downloads: pd.DataFrame, window_days: int = 30) -> dict:
    """Config of the API source: processor rules off, its own periods.

    `downloads`: every saved response (ingest.alerts_in_ua.downloads), not the rows kept after the
    merge by id: a row's request time only says which file holds its latest version. A response
    covers about `window_days` before its request, so the downloads of one oblast cover
    [first request - window_days, last request]. The period is where every oblast is covered: it opens
    at the latest of the oblast starts, ceiled to midnight (the first week is the feature warm-up), and
    data_end is the earliest of the oblast last requests, floored to the hour. An oblast whose
    re-download failed keeps data_end at its previous download instead of looking quiet after it.
    Everything after the warm-up is the evaluation ("test") part.
    """
    uids = [str(u) for u in cfg['api']['oblast_uids']]
    d = downloads[downloads['uid'].isin(uids)]
    missing = sorted(set(uids) - set(d['uid']))
    if missing:
        raise ValueError(f'no saved response for oblast uids {missing}: run scripts/fetch_alerts_in_ua.py')
    cover = d.groupby('uid')['requested_utc'].agg(['min', 'max'])
    c = copy.deepcopy(cfg)
    start = (cover['min'].max() - pd.Timedelta(days=window_days)).ceil('D')
    warm = start + pd.Timedelta(days=7)
    c['processor']['enabled'] = False
    c['data_end'] = cover['max'].min().floor('h').isoformat()
    c['periods'] = {'work_start': start.isoformat(), 'warmup_end': warm.isoformat(),
                    'train_end': warm.isoformat(), 'val_end': warm.isoformat()}
    c['scope']['excluded_oblasts'] = []        # Luhansk is not among the mapped locations at all
    return c


# --- comparison of sources without models (8.4) -------------------------------------------
def unit_profile(art, lo: pd.Timestamp, hi: pd.Timestamp) -> pd.DataFrame:
    """Per target unit on [lo, hi): alerts per day, share of time under alert, median duration."""
    days = (hi - lo).total_seconds() / 86400
    ep = episodes(art.intervals)
    ep = ep[(ep['start_utc'] >= lo) & (ep['start_utc'] < hi)]
    iv = art.intervals
    s = iv['start_utc'].where(iv['start_utc'] > lo, lo)
    e = iv['end_utc'].where(iv['end_utc'] < hi, hi)
    cover = ((e - s).dt.total_seconds().clip(lower=0)).groupby(iv['unit_id']).sum() / (days * 86400)
    tgt = art.units.loc[art.units['role'] == ROLE_TARGET].drop_duplicates('unit_id').set_index('unit_id')
    out = pd.DataFrame({'oblast': tgt['oblast'], 'unit_name': tgt['unit_name']})
    out['alerts_per_day'] = ep.groupby('unit_id').size().reindex(out.index, fill_value=0) / days
    out['share_under_alert'] = cover.reindex(out.index, fill_value=0)
    dur = (ep['end_utc'] - ep['start_utc']).dt.total_seconds() / 60
    out['median_duration_min'] = dur.groupby(ep['unit_id']).median().reindex(out.index)
    return out


def hour_profile(art, lo, hi) -> np.ndarray:
    """Share of episode starts by hour of day in Kyiv time (target units)."""
    ep = episodes(art.intervals)
    tgt = set(art.units.loc[art.units['role'] == ROLE_TARGET, 'unit_id'])
    ep = ep[(ep['start_utc'] >= lo) & (ep['start_utc'] < hi) & ep['unit_id'].isin(tgt)]
    h = ep['start_utc'].dt.tz_convert(KYIV).dt.hour.value_counts().reindex(range(24), fill_value=0)
    return (h / h.sum()).to_numpy()


def clone_jaccard(records: pd.DataFrame, units: pd.DataFrame, lo, hi) -> pd.DataFrame:
    """Minute-level Jaccard of raions inside each clone group (D07) on [lo, hi)."""
    groups = units[units['role'] == ROLE_TARGET].groupby('unit_id')['raion'].apply(list)
    groups = groups[groups.str.len() > 1]
    n = int((hi - lo) // pd.Timedelta(minutes=1))
    rows = []
    for uid, raions in groups.items():
        series = {}
        for r in raions:
            x = records[(records['raion'] == r) & (records['started_at'] < hi) & (records['finished_at'] > lo)]
            a = np.zeros(n + 1, dtype=np.int32)
            s = np.clip((to_sec(x['started_at']) - to_sec(lo)) // 60, 0, n)
            e = np.clip((to_sec(x['finished_at']) - to_sec(lo)) // 60, 0, n)
            np.add.at(a, s, 1)
            np.add.at(a, e, -1)
            series[r] = np.cumsum(a[:-1]) > 0
        for i, r1 in enumerate(raions):
            for r2 in raions[i + 1:]:
                u = (series[r1] | series[r2]).sum()
                rows.append({'unit_id': uid, 'raion1': r1, 'raion2': r2,
                             'jaccard': (series[r1] & series[r2]).sum() / u if u else np.nan})
    return pd.DataFrame(rows)


def volunteer(cfg: dict) -> pd.DataFrame:
    """The volunteer oblast-level series at the pinned commit, read with git show (snapshot untouched)."""
    v = cfg['volunteer']
    blob = subprocess.run(['git', '-C', str(ROOT / cfg['dataset']['repo_dir']), 'show', f"{v['commit']}:{v['path']}"],
                          check=True, capture_output=True).stdout
    if hashlib.sha256(blob).hexdigest() != v['sha256']:
        raise ValueError('SHA-256 mismatch for the volunteer series')
    d = pd.read_csv(io.BytesIO(blob))
    for c in ['started_at', 'finished_at']:
        d[c] = pd.to_datetime(d[c], utc=True).dt.as_unit('s')
    return d.rename(columns={'region': 'oblast'})


def oblast_intervals(art) -> pd.DataFrame:
    """Oblast under alert when at least one of its units (target or input) is: columns oblast, start, end."""
    ob = art.units.drop_duplicates('unit_id').set_index('unit_id')['oblast']
    iv = art.intervals.assign(oblast=art.intervals['unit_id'].map(ob))
    return union(iv.rename(columns={'start_utc': 'start', 'end_utc': 'end'})[['oblast', 'start', 'end']], 'oblast')


def triangulate(src: pd.DataFrame, vol: pd.DataFrame, lo, hi, tol_min: int = 10) -> dict:
    """Agreement of a source with the volunteer series at oblast level on [lo, hi).

    Starts are matched within tol_min minutes; lags of matched starts reveal a time-zone error (a
    shift by whole hours). The hourly cross-correlation of start counts must peak at lag 0.
    """
    v = union(vol[['oblast', 'started_at', 'finished_at']].rename(columns={'started_at': 'start', 'finished_at': 'end'}),
              'oblast')
    common = sorted(set(src['oblast']) & set(v['oblast']))
    s = src[src['oblast'].isin(common) & (src['start'] >= lo) & (src['start'] < hi)]
    v = v[v['oblast'].isin(common) & (v['start'] >= lo) & (v['start'] < hi)]
    tol = tol_min * 60
    lags, matched_src, matched_vol = [], 0, 0
    for ob in common:
        a, b = np.sort(to_sec(s.loc[s['oblast'] == ob, 'start'])), np.sort(to_sec(v.loc[v['oblast'] == ob, 'start']))
        if len(a) == 0 or len(b) == 0:
            continue
        d = _to_nearest(a, b)
        lags += list(d[np.abs(d) <= tol])
        matched_src += int((np.abs(d) <= tol).sum())
        matched_vol += int((np.abs(_to_nearest(b, a)) <= tol).sum())
    hours = pd.date_range(lo, hi, freq='h', inclusive='left')
    cs = s['start'].dt.floor('h').value_counts().reindex(hours, fill_value=0).to_numpy(float)
    cv = v['start'].dt.floor('h').value_counts().reindex(hours, fill_value=0).to_numpy(float)
    xcorr = {lag: float(np.corrcoef(np.roll(cs, lag)[3:-3], cv[3:-3])[0, 1]) for lag in range(-3, 4)}
    return {'oblasts': len(common), 'source_starts': len(s), 'volunteer_starts': len(v),
            'source_starts_matched': matched_src / max(len(s), 1), 'volunteer_starts_matched': matched_vol / max(len(v), 1),
            'median_lag_s': float(np.median(lags)) if lags else np.nan,
            'best_lag_h': max(xcorr, key=xcorr.get), 'xcorr': xcorr}


def _to_nearest(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """For each sorted point of a, a minus the nearest point of sorted, non-empty b."""
    k = np.searchsorted(b, a)
    left, right = b[np.clip(k - 1, 0, len(b) - 1)], b[np.clip(k, 0, len(b) - 1)]
    return np.where(np.abs(right - a) < np.abs(left - a), a - right, a - left)


# --- frozen models (8.5) -------------------------------------------------------------------
def frozen_predictions(train_data: pd.DataFrame, data_end: pd.Timestamp, api_data: pd.DataFrame,
                       h: int, models: dict) -> pd.DataFrame:
    """Fit every model once on source rows with t <= data_end - h; predict the labelled API rows."""
    ycol = f'y_{h}'
    train = train_data[(train_data['t'] <= data_end - pd.Timedelta(hours=h)) & train_data[ycol].notna()]
    test = api_data[(api_data['part'] == 'test') & api_data[ycol].notna()]
    preds = pd.DataFrame({'day': test['t'].dt.floor('D'), 'y': test[ycol].astype(int), 't': test['t'],
                          'unit_id': test['unit_id'], 'oblast': test['oblast'], 'part': 'api'}, index=test.index)
    for name, make in models.items():
        preds[f'p_{name}'] = make().fit(train, train[ycol].to_numpy(dtype=float)).predict_proba(test)
    return preds


def frozen_tables(preds: pd.DataFrame, names: list, cfg: dict, reference: str = 'B1') -> pd.DataFrame:
    bs = cfg['bootstrap']
    return bootstrap(preds, names, bs['n_reps'], bs['seed'], bs['ci'], reference)



def activity(iv: pd.DataFrame, lo: pd.Timestamp, hi: pd.Timestamp, oblasts: list) -> dict:
    """Oblast-level activity on [lo, hi): starts per oblast per day, share of time under alert, hour profile.

    `iv`: oblast intervals (oblast, start, end). Used on both sources and on the volunteer series, so
    that a change between the two windows can be split into a real one (seen by the volunteers in
    both windows) and a difference of sources.
    """
    iv = union(iv[iv['oblast'].isin(oblasts)], 'oblast')
    days = (hi - lo).total_seconds() / 86400
    st = iv[(iv['start'] >= lo) & (iv['start'] < hi)]
    s = iv['start'].where(iv['start'] > lo, lo)
    e = iv['end'].where(iv['end'] < hi, hi)
    cover = (e - s).dt.total_seconds().clip(lower=0).sum() / (len(oblasts) * days * 86400)
    hours = st['start'].dt.tz_convert(KYIV).dt.hour.value_counts().reindex(range(24), fill_value=0)
    return {'starts_per_oblast_day': len(st) / (len(oblasts) * days), 'share_under_alert': cover,
            'hour_profile': (hours / hours.sum()).to_numpy()}


def volunteer_intervals(vol: pd.DataFrame) -> pd.DataFrame:
    return vol.rename(columns={'started_at': 'start', 'finished_at': 'end'})[['oblast', 'start', 'end']]
