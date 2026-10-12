"""The forecast at a chosen moment: the chance that an air-raid alert starts within h hours, per raion.

    python scripts/forecast.py --at "2026-08-27 01:00"                  # Kyiv time, main data (Vadimkin)
    python scripts/forecast.py --at "2026-10-05 20:00" --source api     # alerts.in.ua month, frozen model
    python scripts/forecast.py --at "2026-08-27 01:00" --json           # machine-readable, for a bot or a service
    python scripts/forecast.py --at "2026-08-27 01:00" --h 1 --top 20 --map reports/figures/forecast_example.png

The computation is alerts.forecast.Forecaster (see its docstring): a replay without a look into the
future, with what really happened in the next h hours when the data have it. This script prints it as a
table, or as JSON with --json (only the JSON goes to stdout; logs go to stderr), and can save a csv and a
map. It is not a live forecast: the data end on 7 September (Vadimkin) and on the day of the API download.

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

from alerts import maps  # noqa: E402
from alerts.config import ROOT, load_config  # noqa: E402
from alerts.forecast import KYIV, QUIET, UNDER_ALERT, Forecaster  # noqa: E402
from alerts.pipeline import build_all, model_data  # noqa: E402

logger = logging.getLogger('forecast')
CACHE = ROOT / 'data' / 'cache'


def fingerprint(cfg_file: Path) -> str:
    """Changes when config.yaml or any module under src/ changes: then the cached features are rebuilt."""
    h = hashlib.sha256(cfg_file.read_bytes())
    for f in sorted((ROOT / 'src').rglob('*.py')):
        h.update(f.read_bytes())
    return h.hexdigest()


def model_frame(cfg: dict, rebuild: bool) -> pd.DataFrame:
    """Vadimkin grid rows with features (pipeline.model_data), cached in data/cache/."""
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


def print_table(res, top: int) -> None:
    t, h = res.moment, res.h
    tab = res.table
    quiet = res.quiet.reset_index(drop=True)
    under = tab[tab['status'] == UNDER_ALERT]
    print(f"\nForecast at {t.tz_convert(KYIV):%a %d %b %Y, %H:%M} Kyiv time ({t:%H:%M} UTC), source: {res.source}")
    print(f"Question: will an air-raid alert start in the unit before "
          f"{(t + pd.Timedelta(hours=h)).tz_convert(KYIV):%H:%M} ({h} h)?")
    print(f'LightGBM {res.model}.\n')
    print(f'Under alert now ({len(under)} units): '
          + (', '.join(sorted(under['unit'].str.replace(' raion', ''))) or 'none'))
    n_no = int((tab['status'] == 'no_forecast').sum())
    if n_no:
        print(f'No forecast for {n_no} more (a short pause between alerts or a data gap).')
    if quiet.empty:
        print('\nNo quiet unit has a complete last day of data at this moment (a channel outage, D15).')
        return
    print(f'\nQuiet units, most likely first (top {min(top, len(quiet))} of {len(quiet)}):\n')
    print(f"{'':>3}  {'Unit':<44} {'Oblast':<17} {'LightGBM':>8} {'B1':>5}   What happened")
    for i, r in quiet.head(top).iterrows():
        what = (f"alert at {r['alert_started'].tz_convert(KYIV):%H:%M}" if pd.notna(r['alert_started'])
                else 'no alert' if res.outcome_known else 'unknown (after the end of the data)')
        print(f"{i + 1:>3}  {r['unit'][:44]:<44} {r['oblast'][:17]:<17} {r['p']:>8.0%} {r['p_b1']:>5.0%}   {what}")
    print(f"\nExpected alert starts among {len(quiet)} quiet units (sum of probabilities): {quiet['p'].sum():.1f}", end='')
    if res.outcome_known:
        hit = quiet['alert_started'].notna()
        print(f"; happened: {int(hit.sum())}. Of the top {min(top, len(quiet))}, an alert started in "
              f"{int(hit.head(top).sum())}.")
        brier = lambda p: float(np.mean((p - hit.to_numpy(dtype=float)) ** 2))  # noqa: E731
        print(f"Brier score at this moment: LightGBM {brier(quiet['p']):.3f}, B1 {brier(quiet['p_b1']):.3f} "
              '(lower is better).')
    else:
        print('. What happened is not in the data yet.')


def save_map(res, cfg, units, file) -> None:
    h, t = res.h, res.moment
    tab = res.table
    fm = maps.ForecastMap(maps.map_base(cfg), units, h, f'Will an air-raid alert start within {h} h?',
                          f'Source: {res.source}. LightGBM {res.model}.\nOutlined: an alert did start within '
                          f'{h} h (what happened)' + ('' if res.outcome_known else ' - not known yet, beyond the data') + '.',
                          new_label=f'an alert started within {h} h', quiet_label='no forecast: short pause or data gap')
    q = tab[tab['status'] == QUIET]
    fm.update(maps.Frame(t, {u: True for u in tab.loc[tab['status'] == UNDER_ALERT, 'unit_id']},
                         dict(zip(q['unit_id'], q['p'])),
                         set(tab.loc[tab['alert_started'].notna(), 'unit_id']) if res.outcome_known else set(), set()))
    fm.save(file)
    fm.close()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--at', required=True, help='moment, Kyiv time unless --utc, e.g. "2026-08-27 01:00"')
    ap.add_argument('--utc', action='store_true', help='--at is in UTC')
    ap.add_argument('--h', type=int, default=3, help='horizon in hours: 1, 3 or 6 (default 3)')
    ap.add_argument('--source', choices=['vadimkin', 'api'], default='vadimkin')
    ap.add_argument('--top', type=int, default=15, help='quiet units to list, most likely first')
    ap.add_argument('--json', action='store_true', help='print the forecast of every unit as JSON to stdout')
    ap.add_argument('--map', help='save a map of the forecast and of what happened (png)')
    ap.add_argument('--csv', help='save the forecast of every unit (csv)')
    ap.add_argument('--rebuild', action='store_true', help='rebuild the cached features')
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(name)s: %(message)s')   # stderr
    for name in ['alerts', 'alerts.pipeline', 'alerts.ingest', 'alerts.units', 'alerts.intervals']:
        logging.getLogger(name).setLevel(logging.WARNING)
    t0 = time.time()
    cfg = load_config()
    try:
        fc = Forecaster(cfg, model_frame(cfg, args.rebuild), args.source)
        res = fc.at(args.at, args.h, args.utc)
    except (ValueError, FileNotFoundError) as e:
        ap.error(str(e))

    if args.json:
        sys.stdout.write(res.to_json(indent=1) + '\n')
    else:
        print_table(res, args.top)
    if args.csv:
        res.table.assign(moment_utc=res.moment, h=res.h, source=res.source).to_csv(args.csv, index=False)
        logger.info(f'saved {args.csv}')
    if args.map:
        save_map(res, cfg, fc.units, args.map)
        logger.info(f'saved {args.map}')
    logger.info(f'done in {time.time() - t0:.0f} s')
    return 0


if __name__ == '__main__':
    sys.exit(main())
