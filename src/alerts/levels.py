"""Two-level air-raid alerts, yellow and red, in the alerts.in.ua data (D23). Computation only.

Resolution No. 1092 of the Cabinet of Ministers (4.09.2026) split air-raid alerts into a yellow
level (drone threat) and a red one (missile or combined attack). alerts.in.ua marks every history
record with `alert_level`. Nothing here changes the models, their hyperparameters, the features or
the target (rule 6): the target stays "an alert of any level starts in (t, t+h]", and the level is
used only to split the evaluation afterwards.
"""
import numpy as np
import pandas as pd

from alerts.intervals import episodes
from alerts.metrics import bootstrap
from alerts.scope import ROLE_TARGET, attach_units
from alerts.timeutil import to_sec

LEVELS = ['yellow', 'red']
KEPT_TYPES = ['raion', 'oblast']       # location types the adapter keeps (D22)


# --- step 1: the field ---------------------------------------------------------------------
def field_profile(raw: pd.DataFrame) -> dict:
    """Presence and values of alert_level (and threats) in the history records (read_raw)."""
    has = {c: int(raw[c].notna().sum()) if c in raw else 0 for c in ['alert_level', 'threats']}
    air = raw[raw['alert_type'] == 'air_raid']
    first = raw.groupby('alert_level')['started_at'].agg(['min', 'max', 'size'])
    return {'records': len(raw), 'has': has,
            'values': raw['alert_level'].value_counts(dropna=False).to_dict(),
            'by_alert_type': pd.crosstab(raw['alert_type'], raw['alert_level']),
            'by_location_type': pd.crosstab(air['location_type'], air['alert_level']),
            'started': first}


# --- step 2: transition by oblast ----------------------------------------------------------
def kept_air_raids(raw: pd.DataFrame) -> pd.DataFrame:
    return raw[(raw['alert_type'] == 'air_raid') & raw['location_type'].isin(KEPT_TYPES)]


def transitions(raw: pd.DataFrame) -> pd.DataFrame:
    """Per oblast (Ukrainian name): air-raid records of the kept types by level, first record, first yellow."""
    a = kept_air_raids(raw)
    g = a.groupby('location_oblast')
    out = pd.DataFrame({'records': g.size(),
                        'yellow': g['alert_level'].apply(lambda x: int((x == 'yellow').sum())),
                        'red': g['alert_level'].apply(lambda x: int((x == 'red').sum())),
                        'first_record': g['started_at'].min()})
    out['first_yellow'] = a[a['alert_level'] == 'yellow'].groupby('location_oblast')['started_at'].min()
    out['first_red'] = a[a['alert_level'] == 'red'].groupby('location_oblast')['started_at'].min()
    return out.sort_values('first_yellow')


def weekly(raw: pd.DataFrame) -> pd.DataFrame:
    """Yellow / red records per oblast and week (weeks start on Monday, UTC)."""
    a = kept_air_raids(raw)
    week = a['started_at'].dt.tz_localize(None).dt.to_period('W-SUN').dt.start_time.dt.date.rename('week')
    return a.groupby(['location_oblast', week, 'alert_level']).size().unstack(['week', 'alert_level'], fill_value=0)


# --- step 3: drop rows, metrics again ------------------------------------------------------
def metrics_without(preds: pd.DataFrame, drop: pd.Series, names: list, cfg: dict, reference: str = 'B1') -> dict:
    """The same bootstrap on all rows and on the rows that remain; paired differences from `reference`."""
    bs = cfg['bootstrap']
    run = lambda p: bootstrap(p, names, bs['n_reps'], bs['seed'], bs['ci'], reference)  # noqa: E731
    return {'all': run(preds), 'without': run(preds[~drop])}


# --- step 4: level of the first alert in the window, split by transition ------------------
def record_levels(recs: pd.DataFrame, raw: pd.DataFrame, units: pd.DataFrame) -> pd.DataFrame:
    """Adapter records (load_alerts_in_ua) with their unit and alert_level: unit_id, start (s), level."""
    lvl = raw.set_index('id')['alert_level']
    r = recs.assign(raion=recs['raion'].fillna(recs['oblast']))
    r = attach_units(r, units)
    r = r.assign(level=r['api_id'].map(lvl), start=to_sec(r['started_at']))
    if r['level'].isna().any():
        raise ValueError('adapter records without alert_level')
    return r[['unit_id', 'start', 'level']]


def first_level(rows: pd.DataFrame, rec_levels: pd.DataFrame, h: int) -> pd.Series:
    """Level of the first alert start of the row's unit in (t, t+h]: yellow, red, both (records of the
    unit start in the same second with different levels, e.g. clones) or NA when nothing starts.

    For a grid row (quiet at t, not inside a bridged pause) the first record start after t is the
    first episode start, so `notna()` must equal y_h = 1; the caller checks this.
    """
    lv = (rec_levels.groupby(['unit_id', 'start'])['level']
                    .agg(lambda x: x.iloc[0] if x.nunique() == 1 else 'both').reset_index())
    out = pd.Series(pd.NA, index=rows.index, dtype='object')
    t = pd.Series(to_sec(rows['t']), index=rows.index)
    for u, idx in rows.groupby('unit_id').groups.items():
        g = lv[lv['unit_id'] == u]
        s, lev = g['start'].to_numpy(), g['level'].to_numpy()
        tt = t.loc[idx].to_numpy()
        k = np.searchsorted(s, tt, side='right')              # first start strictly after t
        ok = k < len(s)
        hit = np.zeros(len(tt), dtype=bool)
        hit[ok] = s[k[ok]] <= tt[ok] + h * 3600
        vals = np.full(len(tt), None, dtype=object)
        vals[hit] = lev[k[hit]]
        out.loc[idx] = vals
    return out


def by_level(preds: pd.DataFrame, level: pd.Series, names: list, cfg: dict, reference: str = 'B1') -> pd.DataFrame:
    """Positives by the level of their first alert: share, mean forecast, and ROC-AUC of these
    positives against all negatives (paired bootstrap over days, difference from `reference`)."""
    bs = cfg['bootstrap']
    neg = preds['y'] == 0
    rows = [{'group': 'negatives', 'rows': int(neg.sum()), 'share_of_positives': np.nan,
             **{f'mean_p_{m}': preds.loc[neg, f'p_{m}'].mean() for m in names}}]
    npos = int((preds['y'] == 1).sum())
    for g in ['yellow', 'red', 'both']:
        pos = (preds['y'] == 1) & (level == g)
        if not pos.any():
            continue
        r = {'group': f'positives, first alert {g}', 'rows': int(pos.sum()), 'share_of_positives': pos.sum() / npos,
             **{f'mean_p_{m}': preds.loc[pos, f'p_{m}'].mean() for m in names}}
        tab = bootstrap(preds[neg | pos], names, bs['n_reps'], bs['seed'], bs['ci'], reference)
        for m in names:
            x = tab[(tab['model'] == m) & (tab['metric'] == 'roc_auc')].iloc[0]
            r[f'roc_auc_{m}'] = (x['value'], x['lo'], x['hi'])
            if m != reference:
                r[f'roc_auc_{m}-{reference}'] = (x['diff'], x['diff_lo'], x['diff_hi'])
        rows.append(r)
    return pd.DataFrame(rows)


def split_parts(preds: pd.DataFrame, dates: dict) -> pd.Series:
    """before / after the oblast's transition by the forecast moment t; oblasts not in `dates`: NA.
    A date NaT means no transition seen in the window: every row is 'before'."""
    d = preds['oblast'].map(dates)
    known = preds['oblast'].isin(list(dates))
    part = pd.Series(pd.NA, index=preds.index, dtype='object')
    part[known] = np.where(d[known].notna() & (preds.loc[known, 't'] >= d[known]), 'after', 'before')
    return part


def part_metrics(preds: pd.DataFrame, part: pd.Series, names: list, cfg: dict, reference: str = 'B1') -> dict:
    bs = cfg['bootstrap']
    out = {}
    for p in ['before', 'after']:
        sub = preds[part == p]
        if len(sub):
            out[p] = bootstrap(sub, names, bs['n_reps'], bs['seed'], bs['ci'], reference)
    return out


# --- step 5: regimes without models --------------------------------------------------------
def oblast_profile(art, lo: pd.Timestamp, hi: pd.Timestamp) -> pd.DataFrame:
    """Per oblast of target units on [lo, hi): alerts per unit per day, median duration, share under alert."""
    days = (hi - lo).total_seconds() / 86400
    tgt = art.units[art.units['role'] == ROLE_TARGET].drop_duplicates('unit_id').set_index('unit_id')['oblast']
    ep = episodes(art.intervals)
    ep = ep[(ep['start_utc'] >= lo) & (ep['start_utc'] < hi) & ep['unit_id'].isin(tgt.index)]
    ep = ep.assign(oblast=ep['unit_id'].map(tgt), dur=(ep['end_utc'] - ep['start_utc']).dt.total_seconds() / 60)
    iv = art.intervals[art.intervals['unit_id'].isin(tgt.index)]
    s = iv['start_utc'].where(iv['start_utc'] > lo, lo)
    e = iv['end_utc'].where(iv['end_utc'] < hi, hi)
    cover = (e - s).dt.total_seconds().clip(lower=0).groupby(iv['unit_id'].map(tgt)).sum()
    n_units = tgt.groupby(tgt).size()
    return pd.DataFrame({'units': n_units,
                         'alerts_per_unit_day': ep.groupby('oblast').size().reindex(n_units.index, fill_value=0) / (n_units * days),
                         'median_duration_min': ep.groupby('oblast')['dur'].median(),
                         'share_under_alert': cover.reindex(n_units.index, fill_value=0) / (n_units * days * 86400)})


def raion_jaccard(records: pd.DataFrame, raions: pd.DataFrame, lo: pd.Timestamp, hi: pd.Timestamp) -> pd.DataFrame:
    """Minute-level Jaccard of every pair of raions inside each oblast on [lo, hi).

    `records`: oblast, raion, started_at, finished_at (already filtered to the level wanted);
    `raions`: the (oblast, raion) pairs to compare, so that a raion without records of this level
    still counts. Pairs where neither raion is ever under alert have no Jaccard and are left out.
    """
    n = int((hi - lo) // pd.Timedelta(minutes=1))
    x = records[(records['started_at'] < hi) & (records['finished_at'] > lo)]
    rows = []
    for ob, raions in raions.groupby('oblast')['raion'].unique().items():
        series = {}
        for r in sorted(raions):
            y = x[(x['oblast'] == ob) & (x['raion'] == r)]
            a = np.zeros(n + 1, dtype=np.int32)
            np.add.at(a, np.clip((to_sec(y['started_at']) - to_sec(lo)) // 60, 0, n), 1)
            np.add.at(a, np.clip((to_sec(y['finished_at']) - to_sec(lo)) // 60, 0, n), -1)
            series[r] = np.cumsum(a[:-1]) > 0
        names = sorted(series)
        for i, r1 in enumerate(names):
            for r2 in names[i + 1:]:
                u = (series[r1] | series[r2]).sum()
                if u:
                    rows.append({'oblast': ob, 'raion1': r1, 'raion2': r2,
                                 'jaccard': (series[r1] & series[r2]).sum() / u})
    return pd.DataFrame(rows, columns=['oblast', 'raion1', 'raion2', 'jaccard'])
