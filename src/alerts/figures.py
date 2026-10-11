"""All figures of the reports (data, clones, outage, calibration). Numbers and tables live elsewhere:
alerts.report (stage summaries) and alerts.evaluation (backtest tables).

Palette and marks follow one design method: the first three validated categorical slots, thin
marks, recessive grid, text in ink colours, never in series colours.
"""
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from alerts.config import ts  # noqa: E402
from alerts.intervals import episodes  # noqa: E402
from alerts.scope import ROLE_TARGET  # noqa: E402

# Reference palette of the dataviz method: first three categorical slots (validated all-pairs)
SURFACE, INK, INK_2, GRID, BAND = '#fcfcfb', '#0b0b0b', '#52514e', '#e4e3df', '#d9d8d3'
SERIES = ['#2a78d6', '#eb6834', '#1baf7a']


def style(ax, grid_axis='y'):
    ax.set_facecolor(SURFACE)
    for side in ['top', 'right']:
        ax.spines[side].set_visible(False)
    for side in ['left', 'bottom']:
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=INK_2, labelsize=9, length=0)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def title(fig, title, subtitle):
    fig.text(0.01, 0.985, title, ha='left', va='top', fontsize=13, color=INK, weight='bold')
    fig.text(0.01, 0.94, subtitle, ha='left', va='top', fontsize=9.5, color=INK_2)


def save(fig, file):
    fig.savefig(file, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def stage_figures(art, cfg, out) -> None:
    """Figures of stages 1-2 (data, clones, outage) into `out`."""
    work_start, data_end = ts(cfg['periods']['work_start']), ts(cfg['data_end'])
    _fig_levels(art.df, work_start, out / 'level_transition.png')
    _fig_units(art, cfg, out / 'alerts_per_unit.png')
    _fig_durations(art, cfg, out / 'durations.png')
    _fig_jaccard(art.pairs, cfg['thresholds']['clone_jaccard'], cfg['thresholds']['similar_pairs_report'],
                 out / 'jaccard.png')
    _fig_outage(art, cfg, out / 'outage.png')


def _fig_levels(df, work_start, file):
    d = df[df['started_at'] >= pd.Timestamp('2024-01-01', tz='UTC')]
    month = d['started_at'].dt.tz_localize(None).dt.to_period('M')
    share = pd.crosstab(month, d['level'], normalize='index')[['raion', 'oblast', 'hromada']]
    x = share.index.to_timestamp()
    fig, ax = plt.subplots(figsize=(10, 4.8))
    fig.subplots_adjust(top=0.82, left=0.07, right=0.88, bottom=0.1)
    for col, color in zip(share.columns, SERIES):
        ax.plot(x, share[col], color=color, linewidth=2, label=col)
        ax.text(x[-1] + pd.Timedelta(days=12), share[col].iloc[-1], col, color=INK, fontsize=9, va='center')
    ws = work_start.tz_localize(None)
    ax.axvline(ws, color=INK_2, linewidth=1, linestyle='--')
    ax.text(ws, 1.02, ' work_start 2025-11-07', color=INK_2, fontsize=8.5, va='bottom')
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.legend(frameon=False, fontsize=9, loc='center left', labelcolor=INK)
    style(ax)
    title(fig, 'Raion records replace oblast records by November 2025',
           'Share of records by level per month (all oblasts), 2024-01 to 2026-09')
    save(fig, file)


def _fig_units(art, cfg, file):
    units = art.units[art.units['role'] == ROLE_TARGET]
    ep = episodes(art.intervals)
    ep = ep[(ep['start_utc'] >= ts(cfg['periods']['work_start'])) & (ep['start_utc'] < ts(cfg['data_end']))]
    per_unit = ep.groupby('unit_id').size()
    u = units.drop_duplicates('unit_id').assign(n=lambda x: x['unit_id'].map(per_unit).fillna(0))
    order = u.groupby('oblast')['n'].median().sort_values().index
    y = {ob: i for i, ob in enumerate(order)}
    fig, ax = plt.subplots(figsize=(10, 7.5))
    fig.subplots_adjust(top=0.9, left=0.2, right=0.97, bottom=0.07)
    ax.scatter(u['n'], u['oblast'].map(y), s=36, color=SERIES[0], edgecolors=SURFACE, linewidths=1, zorder=3)
    ax.set_yticks(range(len(order)), [ob.replace(' oblast', '') for ob in order])
    ax.set_xlabel('alert episodes per unit', color=INK_2, fontsize=9)
    style(ax, grid_axis='x')
    med = u.groupby('oblast')['n'].median()
    spread = u.groupby('oblast')['n'].agg(lambda n: n.max() / n.min())
    title(fig, f'Alert frequency varies {med.max() / med.min():.0f}x across oblasts '
                f'and up to {spread.max():.1f}x within one',
           f'Episodes per unit, {cfg["periods"]["work_start"][:10]} to {cfg["data_end"][:10]}; '
           f'one dot per unit ({len(u)} units), oblasts sorted by median')
    save(fig, file)


def _fig_durations(art, cfg, file):
    rec = art.scope_all[(art.scope_all['role'] == ROLE_TARGET)
                        & (art.scope_all['started_at'] >= ts(cfg['periods']['work_start']))]
    hours = rec['duration'] / 3600
    long_h = cfg['thresholds']['long_alert_hours']
    bins = np.logspace(np.log10(hours.min()), np.log10(hours.max()), 60)
    fig, ax = plt.subplots(figsize=(10, 4.8))
    fig.subplots_adjust(top=0.82, left=0.08, right=0.97, bottom=0.12)
    ax.hist(hours, bins=bins, color=SERIES[0], edgecolor=SURFACE, linewidth=0.6)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.axvline(long_h, color=INK_2, linewidth=1, linestyle='--')
    n_long = int((hours > long_h).sum())
    ax.text(long_h * 1.08, ax.get_ylim()[1] * 0.5, f'{long_h} h: {n_long} longer alerts\nmasked, rule (a)',
            color=INK_2, fontsize=8.5, va='top')
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda v, _: f'{v * 3600:.0f} s' if v < 1 / 60 else f'{v * 60:.0f} min' if v < 1 else f'{v:.0f} h'))
    ax.set_xlabel('duration (log scale)', color=INK_2, fontsize=9)
    ax.set_ylabel('records (log scale)', color=INK_2, fontsize=9)
    style(ax)
    title(fig, 'Past 24 hours only a thin tail and a 100-hour spike of lost all-clears remain',
           f'Durations of {len(rec):,} target records since work_start; median '
           f'{hours.median() * 60:.0f} min, p99 {hours.quantile(.99):.1f} h')
    save(fig, file)


def _fig_jaccard(pairs, threshold, report_from, file):
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 4.5), gridspec_kw={'width_ratios': [3, 2]})
    fig.subplots_adjust(top=0.8, left=0.07, right=0.97, bottom=0.13, wspace=0.18)
    a.hist(pairs['jaccard'], bins=np.linspace(0, 1, 51), color=SERIES[0], edgecolor=SURFACE, linewidth=0.6)
    a.set_xlabel('Jaccard similarity, all same-oblast pairs', color=INK_2, fontsize=9)
    a.set_ylabel('pairs', color=INK_2, fontsize=9)
    top = pairs[pairs['jaccard'] >= report_from]
    b.hist(top['jaccard'], bins=np.linspace(report_from, 1, 51), color=SERIES[0], edgecolor=SURFACE, linewidth=0.6)
    b.axvline(threshold, color=INK_2, linewidth=1, linestyle='--')
    b.text(threshold - 0.0005, b.get_ylim()[1] * 0.95, f'merge >= {threshold}', color=INK_2,
           fontsize=8.5, ha='right', va='top')
    b.set_xlabel(f'zoom: pairs >= {report_from}', color=INK_2, fontsize=9)
    for ax in (a, b):
        style(ax)
    n_merge = int((pairs['jaccard'] >= threshold).sum())
    title(fig, 'Similarity of raion series is a continuum; the clone threshold is fixed in advance',
           f'{len(pairs)} same-oblast pairs, train period; {len(top)} pairs >= {report_from}, '
           f'{n_merge} pairs >= {threshold} form the clone groups (D07)')
    save(fig, file)


def _fig_outage(art, cfg, file):
    """Validation and test windows, one bar per day; the outage band is drawn behind the bars."""
    work_start, data_end = ts(cfg['periods']['work_start']), ts(cfg['data_end'])
    val_start, test_start = ts(cfg['periods']['train_end']), ts(cfg['periods']['val_end'])
    df = art.df[(art.df['started_at'] >= work_start) & (art.df['started_at'] < data_end)]
    day = df['started_at'].dt.tz_localize(None).dt.floor('D')
    days = pd.date_range(work_start.tz_localize(None), data_end.tz_localize(None), freq='D', inclusive='left')
    per_day = day.value_counts().reindex(days, fill_value=0)
    shown = per_day[per_day.index >= val_start.tz_localize(None)]
    top = shown.max() * 1.25

    fig, ax = plt.subplots(figsize=(10, 4.5))
    fig.subplots_adjust(top=0.8, left=0.07, right=0.97, bottom=0.1)
    for o in art.outages.itertuples():
        s, e = o.start.tz_localize(None), o.end.tz_localize(None)
        ax.axvspan(s, e, color=BAND, linewidth=0, zorder=0)
        ax.text(s + (e - s) / 2, top * 0.97, f'channel silent\n{(o.end - o.start).total_seconds() / 86400:.1f} days',
                color=INK, fontsize=8.5, ha='center', va='top')
    ax.bar(shown.index + pd.Timedelta(hours=12), shown.to_numpy(), width=0.8, color=SERIES[0], zorder=2)
    for x, label in [(val_start, 'validation'), (test_start, 'test')]:
        x = x.tz_localize(None)
        ax.axvline(x, color=INK_2, linewidth=1, linestyle='--')
        ax.text(x + pd.Timedelta(hours=10), top * 0.97, label, color=INK_2, fontsize=8.5, va='top')
    ax.set_ylim(0, top)
    ax.set_ylabel('alert starts per day, all levels', color=INK_2, fontsize=9)
    style(ax)
    title(fig, 'The channel went silent for four days inside the test window',
           f'Alert starts per day in the whole file; median {per_day.median():.0f} over the working period, '
           f'zero on {int((per_day == 0).sum())} days (D15)')
    save(fig, file)


def calibration(res: dict, file) -> None:
    """Reliability curves of the test part; small multiples, one panel per model."""
    names = res['models']
    fig, axes = plt.subplots(1, len(names), figsize=(3.2 * len(names), 3.6), sharey=True, squeeze=False)
    fig.subplots_adjust(top=0.74, left=0.07, right=0.98, bottom=0.17, wspace=0.12)
    for ax, m in zip(axes[0], names):
        c = res['calibration'][m]
        ax.plot([0, 1], [0, 1], color=INK_2, linewidth=1, linestyle='--')
        ax.plot(c['p_mean'], c['y_rate'], color=SERIES[0], linewidth=2, marker='o', markersize=4)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title(m, color=INK, fontsize=10, loc='left')
        ax.set_xlabel('predicted', color=INK_2, fontsize=9)
        style(ax, grid_axis='both')
    axes[0][0].set_ylabel('observed rate', color=INK_2, fontsize=9)
    title(fig, f'Calibration on the test part, h = {res["h"]}',
           'Ten quantile bins of the prediction; the dashed line is perfect calibration')
    save(fig, file)
