"""Backtest evaluation (PLAN stages 4 and 6; D18): run models, bootstrap, per-oblast tables, calibration.

The reference for paired differences is chosen on the validation part only (lowest log loss among
the baselines), never on the test part (PLAN rule 6).
"""
import logging

import numpy as np
import pandas as pd

from alerts import backtest, figures
from alerts.metrics import METRICS, bootstrap, calibration, score

logger = logging.getLogger(__name__)


def evaluate(data: pd.DataFrame, h: int, models: dict, baselines: list, cfg: dict) -> dict:
    """Backtest every model on val and test; return predictions and all tables."""
    preds = backtest.run(data, h, models, cfg)
    names = list(models)
    bs = cfg['bootstrap']
    val = preds[preds['part'] == 'val']
    reference = min(baselines, key=lambda m: score(val['y'], val[f'p_{m}'])['log_loss'])
    tables = {part: bootstrap(preds[preds['part'] == part], names, bs['n_reps'], bs['seed'], bs['ci'], reference)
              for part in ['val', 'test']}
    test = preds[preds['part'] == 'test']
    vs_lr = (bootstrap(test, names, bs['n_reps'], bs['seed'], bs['ci'], 'LR') if 'LR' in names else None)
    by_oblast = _by_oblast(test, names, reference, bs)
    calib = {m: calibration(test['y'].to_numpy(), test[f'p_{m}'].to_numpy()) for m in names}
    return {'h': h, 'preds': preds, 'reference': reference, 'tables': tables, 'vs_lr': vs_lr,
            'by_oblast': by_oblast, 'calibration': calib, 'models': names,
            'importance': _importance(data, h, models, cfg) if 'LGBM' in models else None}


def _importance(data: pd.DataFrame, h: int, models: dict, cfg: dict) -> pd.Series:
    """Gain importance of the LightGBM model of the last test day (PLAN: gain, not split counts)."""
    last = backtest.days(cfg, 'test')[-1]
    ycol = f'y_{h}'
    train = data[(data['t'] <= last - pd.Timedelta(hours=h)) & data[ycol].notna()]
    return models['LGBM']().fit(train, train[ycol].to_numpy(dtype=float)).gain_importance()


def _by_oblast(test: pd.DataFrame, names: list, reference: str, bs: dict) -> pd.DataFrame:
    rows = []
    for ob, g in test.groupby('oblast'):
        b = bootstrap(g, names, bs['n_reps_oblast'], bs['seed'], bs['ci'], reference)
        b = b[b['metric'].isin(['pr_auc', 'brier'])].assign(oblast=ob, rows=len(g), positives=int(g['y'].sum()))
        rows.append(b)
    return pd.concat(rows, ignore_index=True)


def write_report(res: dict, cfg: dict, out_dir, extra_md: str = '') -> None:
    h, ref, names = res['h'], res['reference'], res['models']
    lines = [f'# Backtest, h = {h}', '',
             'Walk-forward with daily retraining: a model for day D is fitted on rows with t <= D - h. '
             f"Confidence intervals: {int(cfg['bootstrap']['ci'] * 100)}% percentile, "
             f"{cfg['bootstrap']['n_reps']} bootstrap draws of whole forecast days; the same draws for every "
             f'model, so differences are paired. Reference for differences: **{ref}** (best baseline by log loss '
             'on validation). Decisions: DECISIONS.md, D18.', '']
    for part in ['val', 'test']:
        t = res['tables'][part]
        lines += [f'## {part.capitalize()}: {t.attrs["n_rows"]:,} rows, {t.attrs["n_pos"]:,} positives, '
                  f'{t.attrs["n_days"]} days', '',
                  '| Model | ' + ' | '.join(METRICS) + ' |', '|---|' + '---|' * len(METRICS)]
        for m in names:
            r = t[t['model'] == m].set_index('metric')
            lines.append(f'| {m} | ' + ' | '.join(f"{r.at[k, 'value']:.4f} [{r.at[k, 'lo']:.4f}, {r.at[k, 'hi']:.4f}]"
                                                for k in METRICS) + ' |')
        lines += ['', f'Difference from {ref} (model - {ref}); PR-AUC and ROC-AUC: higher is better, '
                  'Brier and log loss: lower is better:', '',
                  '| Model | ' + ' | '.join(METRICS) + ' |', '|---|' + '---|' * len(METRICS)]
        for m in names:
            if m == ref:
                continue
            r = t[t['model'] == m].set_index('metric')
            lines.append(f'| {m} | ' + ' | '.join(
                f"{r.at[k, 'diff']:+.4f} [{r.at[k, 'diff_lo']:+.4f}, {r.at[k, 'diff_hi']:+.4f}]" for k in METRICS) + ' |')
        lines.append('')

    if res['vs_lr'] is not None:
        t = res['vs_lr']
        lines += ['## Test: difference from LR (model - LR)', '',
                  '| Model | ' + ' | '.join(METRICS) + ' |', '|---|' + '---|' * len(METRICS)]
        for m in names:
            if m == 'LR':
                continue
            r = t[t['model'] == m].set_index('metric')
            lines.append(f'| {m} | ' + ' | '.join(
                f"{r.at[k, 'diff']:+.4f} [{r.at[k, 'diff_lo']:+.4f}, {r.at[k, 'diff_hi']:+.4f}]" for k in METRICS) + ' |')
        lines.append('')
    if res['importance'] is not None:
        lines += ['## LightGBM feature importance (gain share, model of the last test day)', '',
                  '| Feature | Gain share |', '|---|---|']
        lines += [f'| {f} | {v:.3f} |' for f, v in res['importance'].items()]
        lines.append('')

    bo = res['by_oblast']
    lines += ['## Test by oblast', '',
              f"{cfg['bootstrap']['n_reps_oblast']} bootstrap draws of days within the oblast. Few positives "
              'mean wide intervals; "—": no positives in the test part, PR-AUC undefined. Within an oblast the '
              'ranking has to separate moments and nearby units, not east from west.', '',
              '| Oblast | Rows | Positives | ' + ' | '.join(f'PR-AUC {m}' for m in names) + ' |',
              '|---|---|---|' + '---|' * len(names)]
    order = bo[bo['metric'] == 'pr_auc'].groupby('oblast')['positives'].first().sort_values().index
    for ob in order:
        g = bo[(bo['oblast'] == ob) & (bo['metric'] == 'pr_auc')].set_index('model')
        lines.append(f"| {ob} | {g['rows'].iloc[0]:,} | {g['positives'].iloc[0]:,} | " + ' | '.join(
            '—' if np.isnan(g.at[m, 'value']) else
            f"{g.at[m, 'value']:.3f} [{g.at[m, 'lo']:.3f}, {g.at[m, 'hi']:.3f}]" for m in names) + ' |')
    lines += ['', f'Calibration on the test part: `figures/calibration_h{h}.png`.', '', extra_md]
    (out_dir / f'backtest_h{h}.md').write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')
    figures.calibration(res, out_dir / 'figures' / f'calibration_h{h}.png')


def write_summary(results: list[dict], cfg: dict, out_dir) -> None:
    """reports/results.md: model x horizon on the test part, with bootstrap intervals (PLAN stage 7)."""
    names = results[0]['models']
    lines = ['# Results: model x horizon (test part)', '',
             'Walk-forward with daily retraining on the test part (2026-08-10 to 2026-09-07, D14). Intervals: '
             f"{int(cfg['bootstrap']['ci'] * 100)}% percentile, {cfg['bootstrap']['n_reps']} bootstrap draws of whole "
             'days; differences are paired (same draws). Hyperparameters chosen on validation for each horizon (D20). '
             'Details per horizon: `backtest_h<h>.md`.', '',
             '## Metrics', '', '| h | Rows | Base rate | Model | PR-AUC | ROC-AUC | Brier | Log loss |',
             '|---|---|---|---|---|---|---|---|']
    for res in results:
        t = res['tables']['test']
        for m in names:
            r = t[t['model'] == m].set_index('metric')
            cell = lambda k: f"{r.at[k, 'value']:.3f} [{r.at[k, 'lo']:.3f}, {r.at[k, 'hi']:.3f}]"  # noqa: E731
            lines.append(f"| {res['h']} | {t.attrs['n_rows']:,} | {t.attrs['n_pos'] / t.attrs['n_rows']:.3f} | {m} | "
                         f"{cell('pr_auc')} | {cell('roc_auc')} | {cell('brier')} | {cell('log_loss')} |")
    lines += ['', '## Difference from the best baseline (chosen on validation)', '',
              '| h | Reference | Model | PR-AUC | Log loss | Brier |', '|---|---|---|---|---|---|']
    for res in results:
        t = res['tables']['test']
        for m in names:
            if m in cfg['backtest']['baselines']:
                continue
            r = t[t['model'] == m].set_index('metric')
            cell = lambda k: f"{r.at[k, 'diff']:+.3f} [{r.at[k, 'diff_lo']:+.3f}, {r.at[k, 'diff_hi']:+.3f}]"  # noqa: E731
            lines.append(f"| {res['h']} | {res['reference']} | {m} | {cell('pr_auc')} | {cell('log_loss')} | "
                         f"{cell('brier')} |")
    lines += ['', 'Figures: `figures/calibration_h<h>.png`, `figures/forecast_vs_fact.png`.']
    (out_dir / 'results.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
