"""One command from scratch: snapshot -> tables (stages 1b-3) -> features -> backtests -> reports.

    python scripts/run_all.py              # everything
    python scripts/run_all.py --no-backtest

Exits with code 1 if a recomputed number differs from the DECISIONS.md reference table or if the
leakage check fails.
"""
import argparse
import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from alerts import figures, leakage, report  # noqa: E402
from alerts.config import load_config, path, ts  # noqa: E402
from alerts.evaluation import evaluate, write_report, write_summary  # noqa: E402
from alerts.models import registry  # noqa: E402
from alerts.pipeline import build_all, model_data, save_all  # noqa: E402
from alerts.spans import union  # noqa: E402
from alerts.tuning import tune  # noqa: E402
from fetch_data import ensure_snapshot  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--no-backtest', action='store_true', help='stop after the tables and their reports')
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(name)s: %(message)s')
    t0 = time.time()
    cfg = load_config()
    ensure_snapshot(cfg)
    art = build_all(cfg)
    save_all(art, cfg)
    failed = bool(report.write_all(art, cfg))

    if not args.no_backtest:
        out = path(cfg, 'reports')
        bt = cfg['backtest']
        data = model_data(art, cfg)
        tuned, summaries = {}, []
        for h in bt['horizons']:
            tuned[h], table = tune(data, h, cfg)
            (out / f'tuning_h{h}.json').write_text(json.dumps(tuned[h], indent=1), encoding='utf-8')
            models = registry(cfg, bt['baselines'] + bt['models'], tuned[h])
            res = evaluate(data, h, models, bt['baselines'], cfg)
            write_report(res, cfg, out, _tuning_md(table))
            res['preds'].to_parquet(str(path(cfg, 'predictions')).format(h=h))
            summaries.append({k: v for k, v in res.items() if k != 'preds'})
            if h == cfg['leakage_check']['horizon']:
                rp = cfg['report']
                outage = union(art.masks[art.masks['reason'] == 'outage'].assign(k=0), 'k')
                figures.forecast_vs_fact(res['preds'], art.intervals, outage, art.units, rp['forecast_units'],
                                         rp['forecast_days'], h, out / 'figures' / 'forecast_vs_fact.png')
        write_summary(summaries, cfg, out)
        lc = cfg['leakage_check']
        models = registry(cfg, bt['baselines'] + bt['models'], tuned.get(lc['horizon']))
        results = []
        checks = {'corrupted_future': lambda c: leakage.check(art.df, cfg, c, lc['horizon'], models),
                  'known_at_cut': lambda c: leakage.knowledge_check(art.df, cfg, c)}
        for cut in lc['cuts']:
            for name, run in checks.items():
                try:
                    results.append({'check': name, **run(ts(cut))})
                except AssertionError as e:
                    logging.error(f'Leakage check {name} failed at {cut}: {e}')
                    results.append({'check': name, 'cut': cut, 'failed': str(e)})
                    failed = True
        (out / 'leakage_check.json').write_text(json.dumps(results, indent=1), encoding='utf-8')
        logging.info(f'Leakage check: {results}')

    logging.info(f'Done in {time.time() - t0:.1f} s')
    return 1 if failed else 0


def _tuning_md(table) -> str:
    cols = [c for c in ['model', 'C', 'num_leaves', 'min_child_samples', 'half_life_days', 'n_estimators',
                        'log_loss', 'pr_auc', 'brier', 'seconds'] if c in table]
    lines = ['## Hyperparameters chosen on validation (D20)', '',
             'Fitted on rows with t <= train_end - h, scored on the validation rows; the lowest log loss wins.', '',
             '| ' + ' | '.join(cols) + ' |', '|' + '---|' * len(cols)]
    ints = {'num_leaves', 'min_child_samples', 'half_life_days', 'n_estimators'}

    def cell(c, v):
        if isinstance(v, float) and v != v:
            return ''
        if c in ints:
            return str(int(v))
        return f'{v:.1f}' if c == 'seconds' else (f'{v:.4f}' if isinstance(v, float) else str(v))

    for _, r in table[cols].sort_values(['model', 'log_loss']).iterrows():
        lines.append('| ' + ' | '.join(cell(c, r[c]) for c in cols) + ' |')
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    sys.exit(main())
