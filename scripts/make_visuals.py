"""Presentation figures: maps of alert levels and raion synchrony, and the animation of alerts with the
forecast (README).

    python scripts/make_visuals.py                    # everything the available data allows
    python scripts/make_visuals.py --only gif         # one of: levels, synchrony, gif

Needs the main pipeline outputs (python scripts/run_all.py). The map of alert levels and the "after"
panel of synchrony need the raw alerts.in.ua responses (scripts/fetch_alerts_in_ua.py); without them
they are skipped with a message. Writes into reports/figures: levels_coverage.png,
raion_synchrony.png, alerts_forecast.gif and its still frame alerts_forecast.png.

Nothing is fitted here: the animation shows the saved walk-forward predictions of the test period
(each day's model saw only the rows known before that day, D18).
"""
import argparse
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from alerts import api_check as ac  # noqa: E402
from alerts import levels as lv  # noqa: E402
from alerts import maps, store  # noqa: E402
from alerts.config import ROOT, load_config, path, ts  # noqa: E402
from alerts.ingest.alerts_in_ua import build_locations, downloads, load_alerts_in_ua, read_raw  # noqa: E402
from alerts.ingest.vadimkin import load_official  # noqa: E402
from alerts.intervals import episodes  # noqa: E402
from alerts.scope import select_scope  # noqa: E402

logger = logging.getLogger('make_visuals')
KYIV = 'Europe/Kyiv'


def api_records(cfg, units):
    """API records with their alert level and the API period, or None when there are no raw responses."""
    raw_dir = ROOT / cfg['api']['raw_dir']
    if not any(raw_dir.glob('*_*.json')):
        logger.warning(f'no raw alerts.in.ua responses in {raw_dir}: the figures that need them are skipped')
        return None
    raw = read_raw(raw_dir)
    recs, _ = load_alerts_in_ua(raw, build_locations(units, cfg))
    recs = recs.assign(raion=recs['raion'].fillna(recs['oblast']), level=recs['api_id'].map(raw.set_index('id')['alert_level']))
    cfg_a = ac.api_config(cfg, downloads(raw_dir))
    return recs, ts(cfg_a['periods']['work_start']), ts(cfg_a['data_end'])


def mean_jaccard(pairs: pd.DataFrame) -> dict:
    both = pd.concat([pairs.rename(columns={'raion1': 'raion', 'raion2': 'other'}),
                      pairs.rename(columns={'raion2': 'raion', 'raion1': 'other'})])
    return both.groupby(['oblast', 'raion'])['jaccard'].mean().to_dict()


def levels_map(cfg, base, units, api, out):
    recs, lo, hi = api
    tgt = units[units['role'] == 'target'][['oblast', 'raion']].drop_duplicates()
    area = dict(zip(base.names, base.area))
    tgt = tgt.assign(area=[area[k] for k in zip(tgt['oblast'], tgt['raion'])]).reset_index(drop=True)
    series = {lvl: lv.minute_series(recs[recs['level'] == lvl], tgt, lo, hi) for lvl in lv.LEVELS}
    many = tgt['oblast'] != 'Kyiv City'                      # coverage needs an oblast of several raions
    cov = {lvl: lv.area_coverage(series[lvl][many.to_numpy()], tgt[many].reset_index(drop=True)) for lvl in lv.LEVELS}
    coverage = pd.DataFrame({lvl: cov[lvl]['area_share'] for lvl in lv.LEVELS})
    for lvl in lv.LEVELS:
        coverage[f'hours_{lvl}'] = cov[lvl]['minutes'] / 60
    overall = {lvl: float((c['area_share'] * c['minutes']).sum() / c.loc[c['minutes'] > 0, 'minutes'].sum())
               for lvl, c in cov.items()}
    keys = list(zip(tgt['oblast'], tgt['raion']))
    moments, state = {}, {}
    for lvl in lv.LEVELS:
        k = int(np.argmax(series[lvl].sum(axis=0)))          # the minute with the most raions at this level
        moments[lvl] = lo + pd.Timedelta(minutes=k)
        state[lvl] = {key: ('red' if series['red'][i, k] else 'yellow' if series['yellow'][i, k] else None)
                      for i, key in enumerate(keys)}
    period = f'{lo:%d %b} - {hi:%d %b %Y}'
    maps.levels_figure(base, units, moments, state, coverage, overall, period, out / 'levels_coverage.png')
    logger.info(f"levels_coverage.png: overall area share yellow {overall['yellow']:.2f}, red {overall['red']:.2f}; "
                f"moments {moments}\n{coverage.round(2).to_string()}")


def synchrony_map(cfg, base, units, api, out):
    raions = units[(units['role'] == 'target') & (units['oblast'] != 'Kyiv City')][['oblast', 'raion']].drop_duplicates()
    p = cfg['periods']
    df = load_official(ROOT / cfg['dataset']['path'], cfg['dataset']['sha256'])
    lo, hi = ts(p['work_start']), ts(p['train_end'])
    before = lv.raion_jaccard(select_scope(df, cfg), raions, lo, hi)
    panels = [(f'Before the alert levels: {lo:%d %b %Y} - {hi:%d %b %Y} (training period, Vadimkin)', mean_jaccard(before))]
    if api is not None:
        recs, alo, ahi = api
        panels.append((f'After: {alo:%d %b} - {ahi:%d %b %Y} (alerts.in.ua, both levels)',
                       mean_jaccard(lv.raion_jaccard(recs, raions, alo, ahi))))
    maps.synchrony_figure(base, units, panels, out / 'raion_synchrony.png')
    med = before.groupby('oblast')['jaccard'].median().sort_values()
    logger.info(f'raion_synchrony.png: median Jaccard by oblast before the levels:\n{med.round(2).to_string()}')


def animation(cfg, base, units, out):
    v = cfg['visuals']
    h = v['horizon']
    intervals, masks = store.load_intervals(cfg), store.load_masks(cfg)
    preds = pd.read_parquet(str(path(cfg, 'predictions')).format(h=h))
    preds = preds[preds['part'] == 'test'].rename(columns={'p_LGBM': 'p'})[['unit_id', 't', 'p']]
    ids = units.loc[units['role'] == 'target', 'unit_id'].drop_duplicates().tolist()

    ep = episodes(intervals)
    lo, hi = ts(cfg['periods']['val_end']), ts(cfg['data_end'])
    ep = ep[(ep['start_utc'] >= lo) & (ep['start_utc'] < hi) & ep['unit_id'].isin(ids)]
    per_day = ep.groupby(ep['start_utc'].dt.tz_convert(KYIV).dt.date).size()
    busiest = per_day.idxmax()
    start = (pd.Timestamp(busiest).tz_localize(KYIV) - pd.Timedelta(hours=v['gif_lead_hours'])).tz_convert('UTC')
    step = pd.Timedelta(minutes=v['gif_frame_minutes'])
    times = pd.date_range(start, start + pd.Timedelta(hours=v['gif_hours']), freq=step, inclusive='left')
    frames, timeline = maps.frames(intervals, masks, preds, ids, times, step)

    fm = maps.ForecastMap(base, units, h, f'Alerts and the {h}-hour forecast, raion by raion',
                          f'Test period, Vadimkin data; {busiest:%d %b %Y} had the most alert starts of the test '
                          f'({per_day.max()}). Forecast: LightGBM retrained daily\non what was known before that day '
                          '(walk-forward backtest), made at the top of each hour for the raions quiet then.',
                          timeline, new_label=f"alert started in the last {v['gif_frame_minutes']} min")
    images = []
    for fr in frames:
        fm.update(fr)
        images.append(fm.image())
    k = int(np.argmax([len(fr.new) for fr in frames]))      # still frame: the onset of the largest wave
    fm.update(frames[k])
    fm.save(out / 'alerts_forecast.png')
    fm.close()
    maps.save_gif(images, out / 'alerts_forecast.gif', v['gif_frame_ms'])
    size = (out / 'alerts_forecast.gif').stat().st_size / 1e6
    logger.info(f'alerts_forecast.gif: {len(images)} frames from {times[0]} ({busiest} busiest, '
                f'{per_day.max()} starts), {size:.1f} MB; still frame {frames[k].t}')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', choices=['levels', 'synchrony', 'gif'])
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(name)s: %(message)s')
    t0 = time.time()
    cfg = load_config()
    out = path(cfg, 'reports') / 'figures'
    units = store.load_units(cfg)
    base = maps.map_base(cfg)
    api = api_records(cfg, units) if args.only in (None, 'levels', 'synchrony') else None
    if args.only in (None, 'levels') and api is not None:
        levels_map(cfg, base, units, api, out)
    if args.only in (None, 'synchrony'):
        synchrony_map(cfg, base, units, api, out)
    if args.only in (None, 'gif'):
        animation(cfg, base, units, out)
    logger.info(f'Done in {time.time() - t0:.0f} s')
    return 0


if __name__ == '__main__':
    sys.exit(main())
