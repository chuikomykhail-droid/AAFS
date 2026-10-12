"""The forecast at a chosen moment: the chance that an air-raid alert starts within h hours, per raion.

    python scripts/forecast.py --at "2026-08-27 01:00"                  # Kyiv time, main data (Vadimkin)
    python scripts/forecast.py --at "2026-10-05 20:00" --source api     # alerts.in.ua month, frozen model
    python scripts/forecast.py --at "2026-08-27 01:00" --h 1 --top 20 --map reports/figures/forecast_example.png

A replay without a look into the future:
  * Vadimkin source (2025-11-14 to 2026-09-07): LightGBM with the hyperparameters of D20 is fitted on
    the rows whose labels were known at the moment (t <= moment - h), like one step of the walk-forward
    backtest, and predicts every unit that is quiet at the moment. B1 is fitted on the same rows.
  * API source (the downloaded alerts.in.ua month): the models frozen on all Vadimkin rows, features
    from the API data (stage 8, D22).
Features come from AlertHistory as of the moment (D16, D21). After the forecast the script shows what
really happened in the next h hours, when the data have it. The moment is rounded down to the hour:
forecasts are made at the top of each hour.

This is not a live forecast: the data end on 7 September (Vadimkin) and on the day of the API download.
A live forecast needs the history of the last week from a live source.

The features of the whole Vadimkin grid take about half a minute to build; they are cached in
data/cache/ (git-ignored) and rebuilt when config.yaml or the code under src/ changes.
"""
import argparse
import hashlib
import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from alerts import api_check as ac  # noqa: E402
from alerts import maps, store  # noqa: E402
from alerts.config import ROOT, load_config, path, ts  # noqa: E402
from alerts.history import AlertHistory  # noqa: E402
from alerts.ingest.alerts_in_ua import build_locations, downloads, load_alerts_in_ua, read_raw  # noqa: E402
from alerts.intervals import episodes  # noqa: E402
from alerts.models.baselines import UnitHourRate  # noqa: E402
from alerts.models.learned import GBMModel  # noqa: E402
from alerts.pipeline import build_all, build_tables, model_data  # noqa: E402
from alerts.timeutil import to_sec  # noqa: E402

logger = logging.getLogger('forecast')
KYIV = 'Europe/Kyiv'
CACHE = ROOT / 'data' / 'cache'


def fingerprint(cfg_file: Path) -> str:
    """Changes when config.yaml or any module under src/ changes: then the cached features are rebuilt."""
    h = hashlib.sha256(cfg_file.read_bytes())
    for f in sorted((ROOT / 'src').rglob('*.py')):
        h.update(f.read_bytes())
    return h.hexdigest()


def vadimkin_data(cfg: dict, rebuild: bool) -> pd.DataFrame:
    file, meta = CACHE / 'model_data_vadimkin.parquet', CACHE / 'model_data_vadimkin.json'
    fp = fingerprint(ROOT / 'config.yaml')
    if not rebuild and file.exists() and meta.exists() and json.loads(meta.read_text())['fingerprint'] == fp:
        return pd.read_parquet(file)
    logger.info('building the features of the whole Vadimkin grid (about half a minute, once)')
    data = model_data(build_all(cfg), cfg)
    CACHE.mkdir(parents=True, exist_ok=True)
    data.to_parquet(file)
    meta.write_text(json.dumps({'fingerprint': fp, 'rows': len(data)}))
    return data


def short_name(name: str) -> str:
    parts = name.split(' + ')
    return parts[0] if len(parts) == 1 else f'{parts[0]} + {len(parts) - 1} more (one unit)'


def parse_moment(text: str, utc: bool) -> pd.Timestamp:
    t = pd.Timestamp(text)
    if t.tzinfo is None:
        t = t.tz_localize('UTC' if utc else KYIV, ambiguous=False, nonexistent='shift_forward')
    return t.tz_convert('UTC').floor('h').as_unit('s')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--at', required=True, help='moment, Kyiv time unless --utc, e.g. "2026-08-27 01:00"')
    ap.add_argument('--utc', action='store_true', help='--at is in UTC')
    ap.add_argument('--h', type=int, default=3, help='horizon in hours: 1, 3 or 6 (default 3)')
    ap.add_argument('--source', choices=['vadimkin', 'api'], default='vadimkin')
    ap.add_argument('--top', type=int, default=15, help='quiet units to list, most likely first')
    ap.add_argument('--map', help='save a map of the forecast and of what happened (png)')
    ap.add_argument('--csv', help='save the forecast of every unit (csv)')
    ap.add_argument('--rebuild', action='store_true', help='rebuild the cached features')
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(name)s: %(message)s')
    for name in ['alerts', 'alerts.pipeline', 'alerts.ingest', 'alerts.units', 'alerts.intervals']:
        logging.getLogger(name).setLevel(logging.WARNING)
    t0 = time.time()
    cfg = load_config()
    h = args.h
    if h not in cfg['horizons']:
        ap.error(f'--h must be one of {cfg["horizons"]}')
    ycol = f'y_{h}'
    t = parse_moment(args.at, args.utc)
    units = store.load_units(cfg)
    tuned = json.loads((path(cfg, 'reports') / f'tuning_h{h}.json').read_text(encoding='utf-8'))
    raw_dir = ROOT / cfg['api']['raw_dir']
    if args.source == 'vadimkin':
        lo = ts(cfg['periods']['warmup_end']) + pd.Timedelta(days=cfg['visuals']['forecast_min_train_days'])
        hi = ts(cfg['data_end'])
    else:
        if not any(raw_dir.glob('*_*.json')):
            ap.error(f'no alerts.in.ua responses in {raw_dir}: run scripts/fetch_alerts_in_ua.py with your own token')
        run_cfg = ac.api_config(cfg, downloads(raw_dir))
        lo, hi = ts(run_cfg['periods']['warmup_end']), ts(run_cfg['data_end'])
    if not lo <= t < hi:
        ap.error(f'--at must be in [{lo.tz_convert(KYIV):%Y-%m-%d %H:%M}, {hi.tz_convert(KYIV):%Y-%m-%d %H:%M}) '
                 f'Kyiv time for the {args.source} source')

    data_v = vadimkin_data(cfg, args.rebuild)
    if args.source == 'vadimkin':
        data = data_v
        seen, intervals, masks = store.load_seen(cfg), store.load_intervals(cfg), store.load_masks(cfg)
        train = data_v[(data_v['t'] <= t - pd.Timedelta(hours=h)) & data_v[ycol].notna()]
        how = f'fitted on the {len(train):,} rows whose labels were known at the moment (t <= moment - {h} h)'
    else:
        recs, _ = load_alerts_in_ua(read_raw(raw_dir), build_locations(units, cfg))
        art = build_tables(recs, run_cfg, units=units, neighbors=pd.read_csv(path(cfg, 'neighbors')))
        data, seen, intervals, masks = model_data(art, run_cfg), art.seen, art.intervals, art.masks
        train = data_v[(data_v['t'] <= ts(cfg['data_end']) - pd.Timedelta(hours=h)) & data_v[ycol].notna()]
        how = f'frozen: fitted once on all {len(train):,} Vadimkin rows up to 7 Sep (stage 8); features from the API'

    rows = data[data['t'] == t]
    ids = units.loc[units['role'] == 'target', 'unit_id'].drop_duplicates().tolist()
    names = units.drop_duplicates('unit_id').set_index('unit_id')
    if len(rows) == 0:
        print(f'No forecast at {t.tz_convert(KYIV):%d %b %Y %H:%M} Kyiv time: no quiet unit has a complete '
              'last day of data (a channel outage, D15).')
        return 1
    y = train[ycol].to_numpy(dtype=float)
    p_lgbm = GBMModel(cfg, tuned['LGBM']).fit(train, y).predict_proba(rows)
    p_b1 = UnitHourRate(cfg).fit(train, y).predict_proba(rows)

    # what happened: the first alert start in (t, t+h], when the data reach that far
    ep = episodes(intervals)
    known = t + pd.Timedelta(hours=h) <= hi
    first = {}
    for u, g in ep[(ep['start_utc'] > t) & (ep['start_utc'] <= t + pd.Timedelta(hours=h))].groupby('unit_id'):
        first[u] = g['start_utc'].min()
    under = AlertHistory(seen, intervals, units['unit_id'].drop_duplicates().tolist(), masks).active(pd.DatetimeIndex([t]))[0]
    active = {u for u, a in zip(units['unit_id'].drop_duplicates(), under) if a and u in ids}

    out = pd.DataFrame({'unit_id': rows['unit_id'].to_numpy(), 'p_lgbm': p_lgbm, 'p_b1': p_b1})
    out['unit'] = out['unit_id'].map(names['unit_name']).map(short_name)
    out['oblast'] = out['unit_id'].map(names['oblast']).str.replace(' oblast', '')
    out['alert_started'] = out['unit_id'].map(first)
    out = out.sort_values('p_lgbm', ascending=False).reset_index(drop=True)

    tk = t.tz_convert(KYIV)
    end = (t + pd.Timedelta(hours=h)).tz_convert(KYIV)
    print(f'\nForecast at {tk:%a %d %b %Y, %H:%M} Kyiv time ({t:%H:%M} UTC), source: {args.source}')
    print(f'Question: will an air-raid alert start in the unit before {end:%H:%M} ({h} h)?')
    print(f'LightGBM {how}.\n')
    no_fc = sorted(set(ids) - set(out['unit_id']) - active)
    print(f'Under alert now ({len(active)} units): '
          + (', '.join(sorted(short_name(names.at[u, 'unit_name']).replace(' raion', '') for u in active)) or 'none'))
    if no_fc:
        print(f'No forecast for {len(no_fc)} more (a short pause between alerts or a data gap).')
    print(f'\nQuiet units, most likely first (top {min(args.top, len(out))} of {len(out)}):\n')
    print(f"{'':>3}  {'Unit':<44} {'Oblast':<17} {'LightGBM':>8} {'B1':>5}   What happened")
    for i, r in out.head(args.top).iterrows():
        what = (f"alert at {r['alert_started'].tz_convert(KYIV):%H:%M}" if pd.notna(r['alert_started'])
                else 'no alert' if known else 'unknown (after the end of the data)')
        print(f"{i + 1:>3}  {r['unit'][:44]:<44} {r['oblast'][:17]:<17} {r['p_lgbm']:>8.0%} {r['p_b1']:>5.0%}   {what}")
    print(f"\nExpected alert starts among {len(out)} quiet units (sum of probabilities): {out['p_lgbm'].sum():.1f}", end='')
    if known:
        hit = out['alert_started'].notna()
        top = out.head(args.top)['alert_started'].notna().sum()
        print(f"; happened: {int(hit.sum())}. Of the top {min(args.top, len(out))}, an alert started in {top}.")
        brier = lambda p: float(np.mean((p - hit.to_numpy(dtype=float)) ** 2))  # noqa: E731
        print(f"Brier score at this moment: LightGBM {brier(out['p_lgbm']):.3f}, B1 {brier(out['p_b1']):.3f} (lower is better).")
    else:
        print('. What happened is not in the data yet.')

    if args.csv:
        out.assign(moment_utc=t, h=h, source=args.source).to_csv(args.csv, index=False)
        print(f'Saved {args.csv}')
    if args.map:
        fm = maps.ForecastMap(maps.map_base(cfg), units, h, f'Will an air-raid alert start within {h} h?',
                              f'Source: {args.source}. LightGBM {how}.\nOutlined: an alert did start within '
                              f'{h} h (what happened)' + ('' if known else ' - not known yet, beyond the data') + '.',
                              new_label=f'an alert started within {h} h',
                              quiet_label='no forecast: short pause or data gap')
        fm.update(maps.Frame(t, {u: True for u in active}, dict(zip(out['unit_id'], out['p_lgbm'])),
                             set(first) if known else set(), set()))
        fm.save(args.map)
        fm.close()
        print(f'Saved {args.map}')
    logger.info(f'done in {time.time() - t0:.0f} s')
    return 0


if __name__ == '__main__':
    sys.exit(main())
