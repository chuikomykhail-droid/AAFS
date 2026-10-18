"""Post-submission analysis: B3 (B1 with exponential weights, half-life 7 days) on the test part.

    python scripts/post_submission_b3.py

Protocol and predictions: reports/post_submission/PREREGISTRATION.md (committed before this ran).
Needs the outputs of python scripts/run_all.py: data/predictions_h{1,3,6}.parquet. Nothing is refitted
except B3 and the project's B1 (a sanity check of the harness); LightGBM, LR, B0-B2 are read as saved.
Writes reports/post_submission/b3_test.md and b3_test.json. Stops before writing if a check fails.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from alerts import backtest  # noqa: E402
from alerts.config import ROOT, load_config, ts  # noqa: E402
from alerts.metrics import METRICS, bootstrap  # noqa: E402
from alerts.models.baselines import UnitHourRate  # noqa: E402
from alerts.pipeline import build_all, model_data  # noqa: E402

HALF_LIFE_DAYS = 7                       # fixed by the review before any result (F23); not varied
HORIZONS = [1, 3, 6]
OUT = ROOT / 'reports' / 'post_submission'
ORDINARY_DAYS_END = '2026-08-26'         # secondary analysis of the pre-registration (F25 split)

# Checks (PREREGISTRATION.md)
TEST_ROWS = {1: 46_574, 3: 46_270, 6: 45_767}
README_LGBM_MINUS_B1 = {1: 0.036, 3: 0.027, 6: 0.018}           # PR-AUC, README / results.md
REVIEW_B3_VALIDATION_PR_AUC = {1: 0.4129, 3: 0.6969, 6: 0.8402}  # reviews/FINAL.md section 4
# Predictions written before running: LightGBM - B3, (PR-AUC, log loss)
PREDICTED = {1: (0.035, -0.016), 3: (0.020, -0.007), 6: (0.010, 0.003)}


class ExpUnitHourRate:
    """B3: B1 (unit x hour of day, hierarchical additive smoothing) on all training rows, weight
    0.5 ** (age_days / half_life), the age counted from the last training row."""
    name = 'B3'

    def __init__(self, cfg: dict):
        self.prior = cfg['baselines']['prior_strength']

    def fit(self, X: pd.DataFrame, y: np.ndarray):
        age = (X['t'].max() - X['t']).dt.total_seconds().to_numpy() / 86400
        w = 0.5 ** (age / HALF_LIFE_DAYS)
        d = pd.DataFrame({'u': X['unit_id'].to_numpy(), 'hr': X['hour_kyiv'].to_numpy().astype(int),
                          'wy': w * y, 'w': w})
        self.global_ = d['wy'].sum() / d['w'].sum()
        u = d.groupby('u')[['wy', 'w']].sum()
        self.unit_ = (u['wy'] + self.prior * self.global_) / (u['w'] + self.prior)
        c = d.groupby(['u', 'hr'])[['wy', 'w']].sum()
        parent = self.unit_.reindex(c.index.get_level_values('u')).to_numpy()
        self.cell_ = (c['wy'] + self.prior * parent) / (c['w'] + self.prior)
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        unit = self.unit_.reindex(X['unit_id'].to_numpy()).to_numpy()
        unit = np.where(np.isnan(unit), self.global_, unit)
        key = pd.MultiIndex.from_arrays([X['unit_id'].to_numpy(), X['hour_kyiv'].to_numpy().astype(int)])
        p = self.cell_.reindex(key).to_numpy()
        return np.where(np.isnan(p), unit, p)


def table(b: pd.DataFrame, models: list, diff: bool) -> list:
    """Markdown rows for the metrics (diff=False) or the paired differences (diff=True) of `models`."""
    head = '| Model | ' + ' | '.join(METRICS) + ' |'
    rows = [head, '|---|' + '---|' * len(METRICS)]
    for m in models:
        r = b[b['model'] == m].set_index('metric')
        if diff:
            cells = [f"{r.at[k, 'diff']:+.4f} [{r.at[k, 'diff_lo']:+.4f}, {r.at[k, 'diff_hi']:+.4f}]" for k in METRICS]
        else:
            cells = [f"{r.at[k, 'value']:.4f} [{r.at[k, 'lo']:.4f}, {r.at[k, 'hi']:.4f}]" for k in METRICS]
        rows.append(f'| {m} | ' + ' | '.join(cells) + ' |')
    return rows


def cell(b: pd.DataFrame, model: str, metric: str) -> dict:
    r = b[(b['model'] == model) & (b['metric'] == metric)].iloc[0]
    return {'diff': float(r['diff']), 'lo': float(r['diff_lo']), 'hi': float(r['diff_hi'])}


def main() -> int:
    cfg = load_config()
    bs = cfg['bootstrap']
    data = model_data(build_all(cfg), cfg)
    days = backtest.days(cfg, 'val').append(backtest.days(cfg, 'test'))
    results, checks, report = {}, [], []

    def check(name: str, ok: bool, detail: str):
        checks.append({'check': name, 'ok': bool(ok), 'detail': detail})
        print(('PASS ' if ok else 'FAIL ') + f'{name}: {detail}')

    for h in HORIZONS:
        P = pd.read_parquet(ROOT / 'data' / f'predictions_h{h}.parquet')
        for name, cls in [('B1', UnitHourRate), ('B3', ExpUnitHourRate)]:
            wf = backtest.walk_forward(data, h, days, lambda c=cls: c(cfg)).set_index('row')
            P[f'p_{name}_new'] = wf['p']
        assert P[['p_B1_new', 'p_B3_new']].notna().all().all(), 'missing predictions'
        gap = float(np.abs(P['p_B1_new'] - P['p_B1']).max())
        check(f'h={h} 1. project B1 refitted == saved p_B1', gap == 0.0, f'max |diff| = {gap:.2e}')
        P['p_B3'] = P['p_B3_new']
        val, test = P[P['part'] == 'val'], P[P['part'] == 'test']
        check(f'h={h} 2. test rows and days', len(test) == TEST_ROWS[h] and test['day'].nunique() in (23, 24),
              f'{len(test):,} rows, {test["day"].nunique()} days')

        models = ['B1', 'B3', 'LR', 'LGBM']
        t_b1 = bootstrap(test, models, bs['n_reps'], bs['seed'], bs['ci'], 'B1')
        got = round(cell(t_b1, 'LGBM', 'pr_auc')['diff'], 3)
        check(f'h={h} 3. LightGBM - B1 reproduces README (PR-AUC)', got == README_LGBM_MINUS_B1[h],
              f'{got:+.3f} vs README {README_LGBM_MINUS_B1[h]:+.3f}')
        v_b3 = bootstrap(val, models, bs['n_reps'], bs['seed'], bs['ci'], 'B3')
        b3_val = float(v_b3[(v_b3['model'] == 'B3') & (v_b3['metric'] == 'pr_auc')]['value'].iloc[0])
        check(f'h={h} 4. B3 on validation reproduces the review (PR-AUC)',
              abs(b3_val - REVIEW_B3_VALIDATION_PR_AUC[h]) < 5e-5,
              f'{b3_val:.4f} vs review {REVIEW_B3_VALIDATION_PR_AUC[h]:.4f}')

        t_b3 = bootstrap(test, models, bs['n_reps'], bs['seed'], bs['ci'], 'B3')
        results[h] = {'rows': len(test), 'positives': int(test['y'].sum()), 'days': int(test['day'].nunique()),
                      'lgbm_minus_b3': {k: cell(t_b3, 'LGBM', k) for k in METRICS},
                      'lr_minus_b3': {k: cell(t_b3, 'LR', k) for k in METRICS},
                      'b3_minus_b1': {k: cell(t_b1, 'B3', k) for k in METRICS},
                      'lgbm_minus_b1': {k: cell(t_b1, 'LGBM', k) for k in METRICS},
                      'metrics': {m: {k: float(t_b3[(t_b3['model'] == m) & (t_b3['metric'] == k)]['value'].iloc[0])
                                      for k in METRICS} for m in models}}
        if h == 3:
            ordinary = test[test['day'] <= ts(ORDINARY_DAYS_END + 'T00:00:00Z')]
            o = bootstrap(ordinary, models, bs['n_reps'], bs['seed'], bs['ci'], 'B3')
            results[h]['ordinary_days'] = {'days': int(ordinary['day'].nunique()), 'rows': len(ordinary),
                                           'lgbm_minus_b3': {k: cell(o, 'LGBM', k) for k in METRICS}}
            report_ordinary = (ordinary['day'].nunique(), o)
        report += [f'## h = {h}', '',
                   f'Test: {len(test):,} rows, {int(test["y"].sum()):,} positives, {test["day"].nunique()} days. '
                   f'Brackets: 95% bootstrap over days.', '', '### Metrics', '', *table(t_b3, models, False), '',
                   '### Difference from B3 (model - B3; PR-AUC and ROC-AUC: higher is better, Brier and log loss: lower)',
                   '', *table(t_b3, ['B1', 'LR', 'LGBM'], True), '',
                   '### B3 - B1 (what the stronger baseline gains over the submitted reference)', '',
                   *table(t_b1, ['B3'], True), '']
        if h == 3:
            n, o = report_ordinary
            report += [f'### Secondary: ordinary days of the test part (2026-08-10 to {ORDINARY_DAYS_END}, {n} days), '
                       'difference from B3', '', *table(o, ['B1', 'LR', 'LGBM'], True), '']

    if not all(c['ok'] for c in checks):
        print('A check failed: nothing is written. Fix the cause; do not read the numbers.')
        return 1

    pr_rows = ['## Predictions against facts (LightGBM - B3)', '',
               '| h | Predicted PR-AUC / log loss | Observed PR-AUC | Observed log loss | Advantage shown? |',
               '|---|---|---|---|---|']
    verdict = {}
    for h in HORIZONS:
        pr, ll = results[h]['lgbm_minus_b3']['pr_auc'], results[h]['lgbm_minus_b3']['log_loss']
        shown = pr['lo'] > 0 and ll['hi'] < 0
        verdict[h] = shown
        pr_rows.append(f'| {h} | {PREDICTED[h][0]:+.3f} / {PREDICTED[h][1]:+.3f} | '
                       f"{pr['diff']:+.4f} [{pr['lo']:+.4f}, {pr['hi']:+.4f}] | "
                       f"{ll['diff']:+.4f} [{ll['lo']:+.4f}, {ll['hi']:+.4f}] | {'yes' if shown else 'no'} |")
    rule = ('"Shown" only if the 95% interval of LightGBM - B3 excludes zero for PR-AUC (above) and for log loss '
            '(below), as fixed in the pre-registration.')
    md = ['# B3 (B1 with exponential weights, half-life 7 days) on the test part', '',
          'Post-submission analysis. Protocol and predictions were committed before this ran: '
          '`PREREGISTRATION.md`. B3 is the reference baseline by the project\'s own rule (lowest log loss on '
          'validation). Nothing here changes the submitted results.', '',
          '## Checks', '', *[f"- {'PASS' if c['ok'] else 'FAIL'} {c['check']}: {c['detail']}" for c in checks], '',
          *pr_rows, '', rule, '', *report]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'b3_test.md').write_text('\n'.join(md).rstrip() + '\n', encoding='utf-8')
    (OUT / 'b3_test.json').write_text(json.dumps({'checks': checks, 'verdict': verdict, 'results': results},
                                                 indent=1), encoding='utf-8')
    print(f'Written {OUT / "b3_test.md"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
