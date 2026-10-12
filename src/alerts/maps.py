"""Maps of raions for the presentation: alert levels (D23), raion synchrony (D07, D23), the animation of
alerts with the 3-hour forecast, and the snapshot of scripts/forecast.py.

Geometry: the pinned admin-2 boundaries (geo.boundaries). Coordinates are rounded to
visuals.map_decimals degrees and consecutive duplicates are dropped; the boundaries are topologically
consistent, so both sides of a shared border round to the same points. Oblast borders are the edges
whose raions belong to different oblasts, or to one raion only (the state border). Lon / lat are drawn
with the aspect 1 / cos(mean latitude), enough for a country of this size. Features are drawn from the
largest to the smallest, so a raion lying inside another one (Kyiv) stays on top.

Colours follow the method of alerts.figures: one blue ramp for magnitudes (probability, Jaccard), the
status yellow and red for the alert levels and for "under alert", always with a text label.
"""
from collections import defaultdict
from dataclasses import dataclass

import matplotlib

matplotlib.use('Agg')
import matplotlib.dates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402
from matplotlib.collections import LineCollection, PathCollection  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.path import Path  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from alerts.figures import INK, INK_2, SURFACE, style  # noqa: E402
from alerts.geo import boundaries  # noqa: E402
from alerts.intervals import episodes  # noqa: E402
from alerts.mask import OUTAGE  # noqa: E402
from alerts.spans import count_in, covers, union  # noqa: E402
from alerts.timeutil import to_sec  # noqa: E402

KYIV = 'Europe/Kyiv'
BLUE = ['#cde2fb', '#b7d3f6', '#9ec5f4', '#86b6ef', '#6da7ec', '#5598e7', '#3987e5', '#2a78d6', '#256abf',
        '#1c5cab', '#184f95', '#104281', '#0d366b']                     # sequential ramp, steps 100-700
RAMP = LinearSegmentedColormap.from_list('blue', BLUE)
YELLOW, RED = '#fab219', '#d03b3b'                                       # status warning / critical
QUIET, OUTSIDE, BORDER, MUTED = '#f0efec', '#e6e5e0', '#c3c2b7', '#898781'


@dataclass
class MapBase:
    names: list            # (oblast, raion) per feature, our naming (geo)
    paths: list            # matplotlib Path per feature, exterior rings only
    area: np.ndarray       # km2 per feature
    order: np.ndarray      # drawing order: largest first
    oblast_edges: np.ndarray   # (n, 2, 2) segments of oblast and state borders
    aspect: float


def map_base(cfg: dict) -> MapBase:
    features, names = boundaries(cfg)
    dec = cfg['visuals']['map_decimals']
    paths, owners, lat = [], defaultdict(list), []
    for i, ft in enumerate(features):
        g = ft['geometry']
        polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
        rings = []
        for poly in polys:
            r = np.round(np.asarray(poly[0], dtype=float), dec)
            r = r[np.r_[True, np.any(np.diff(r, axis=0) != 0, axis=1)]]
            if len(r) >= 4:
                rings.append(r)
                lat.append(r[:, 1].mean())
                for a, b in zip(map(tuple, r[:-1]), map(tuple, r[1:])):
                    owners[(a, b) if a <= b else (b, a)].append(names[i][0])
        paths.append(Path.make_compound_path(*[Path(r, closed=True) for r in rings]))
    edges = [k for k, obs in owners.items() if len(obs) == 1 or len(set(obs)) > 1]
    area = np.array([ft['properties']['area_sqkm'] for ft in features], dtype=float)
    return MapBase(names, paths, area, np.argsort(-area), np.array(edges),
                   1 / np.cos(np.deg2rad(np.mean(lat))))


def draw(ax, base: MapBase, colors: list, hatch_mask=None) -> PathCollection:
    """Raions filled with `colors` (one per feature), thin surface-coloured raion borders, oblast borders.
    Features with hatch_mask True get a hatched neutral fill (outside the forecast). Returns the fill
    collection in drawing order (base.order) for updating."""
    o = base.order
    fill = PathCollection([base.paths[i] for i in o], facecolors=[colors[i] for i in o],
                          edgecolors=SURFACE, linewidths=0.35)
    ax.add_collection(fill)
    if hatch_mask is not None and np.any(hatch_mask):
        idx = [i for i in o if hatch_mask[i]]
        ax.add_collection(PathCollection([base.paths[i] for i in idx], facecolors=OUTSIDE, edgecolors=BORDER,
                                         linewidths=0, hatch='////'))
    ax.add_collection(LineCollection(base.oblast_edges, colors=INK_2, linewidths=0.6))
    xy = np.concatenate([p.vertices for p in base.paths])
    ax.set_xlim(xy[:, 0].min() - 0.2, xy[:, 0].max() + 0.2)
    ax.set_ylim(xy[:, 1].min() - 0.2, xy[:, 1].max() + 0.2)
    ax.set_aspect(base.aspect)
    ax.axis('off')
    return fill


def feature_units(base: MapBase, units: pd.DataFrame) -> list:
    """unit_id of every feature (target units only; None outside the forecast)."""
    t = units[units['role'] == 'target']
    key = dict(zip(zip(t['oblast'], t['raion']), t['unit_id']))
    return [key.get(n) for n in base.names]


def _legend(ax, handles, loc='lower left', **kw):
    lg = ax.legend(handles=handles, loc=loc, frameon=False, fontsize=8.5, labelcolor=INK_2,
                   handlelength=1.4, handleheight=1.1, **kw)
    return lg


def _prob_bar(fig, rect, label, percent=True):
    cax = fig.add_axes(rect)
    cb = fig.colorbar(plt.cm.ScalarMappable(cmap=RAMP, norm=plt.Normalize(0, 1)), cax=cax, orientation='horizontal')
    cb.set_ticks([0, 0.25, 0.5, 0.75, 1])
    cb.set_ticklabels(['0', '25%', '50%', '75%', '100%'] if percent else ['0', '0.25', '0.5', '0.75', '1'])
    cb.outline.set_visible(False)
    cax.tick_params(labelsize=8, colors=INK_2, length=0)
    cax.set_title(label, fontsize=8.5, color=INK_2, loc='left', pad=3)
    return cax


# --- D23: what part of an oblast an alert covers -------------------------------------------
def levels_figure(base: MapBase, units: pd.DataFrame, moments: dict, state: dict, coverage: pd.DataFrame,
                  overall: dict, period: str, file) -> None:
    """Two maps (the moments with the most raions under a yellow and under a red alert) and, per oblast,
    the share of its area under alert while at least one of its raions is under an alert of that level.

    moments: {'yellow': ts, 'red': ts}; state: {'yellow': {(oblast, raion): level or None}, 'red': ...}
    (the level of every raion at that moment); coverage: per oblast columns yellow, red (area shares),
    hours_yellow, hours_red; overall: {'yellow': x, 'red': y} (time-weighted over oblasts)."""
    fig = plt.figure(figsize=(13.2, 9.0), facecolor=SURFACE)
    fig.text(0.012, 0.988, 'An air-raid alert rarely covers the whole oblast', ha='left', va='top',
             fontsize=15, color=INK, weight='bold')
    fig.text(0.012, 0.955, f"alerts.in.ua, {period}. While any raion of an oblast is under alert, on average "
             f"{overall['yellow']:.0%} of the oblast's area is under a yellow alert (drone threat) and "
             f"{overall['red']:.0%} under a red one (missile\nor combined attack). "
             'A red alert covers the whole oblast only in the west, where the month had three red waves. '
             'That is why the forecast is made per raion, not per oblast (D23).',
             ha='left', va='top', fontsize=9.5, color=INK_2, linespacing=1.45)
    inside = np.array([u is not None for u in feature_units(base, units)])
    for lvl, y0 in [('yellow', 0.475), ('red', 0.03)]:
        ax = fig.add_axes([0.0, y0, 0.6, 0.37])
        st = state[lvl]
        colors = [{'yellow': YELLOW, 'red': RED}.get(st.get(n), QUIET) for n in base.names]
        draw(ax, base, colors, hatch_mask=~inside)
        n_y = sum(v == 'yellow' for v in st.values())
        n_r = sum(v == 'red' for v in st.values())
        when = moments[lvl].tz_convert(KYIV)
        ax.set_title(f"The largest {lvl} wave of the month: {when:%d %b, %H:%M} Kyiv time\n"
                     f"{n_y} raion{'s' if n_y != 1 else ''} under a yellow alert, {n_r} under a red one",
                     loc='left', fontsize=9.5, color=INK, pad=4, linespacing=1.4)
    fig.legend(handles=[Patch(facecolor=YELLOW, label='yellow alert'), Patch(facecolor=RED, label='red alert'),
                        Patch(facecolor=QUIET, edgecolor=BORDER, label='no alert'),
                        Patch(facecolor=OUTSIDE, edgecolor=BORDER, hatch='////', label='outside the forecast')],
               loc='lower left', bbox_to_anchor=(0.02, 0.43), ncol=4, frameon=False, fontsize=8.5,
               labelcolor=INK_2, handlelength=1.4, handleheight=1.1)

    ax = fig.add_axes([0.70, 0.1, 0.2, 0.73])
    c = coverage.assign(gap=coverage['red'] - coverage['yellow']).sort_values('gap', ascending=True, na_position='last')
    y = np.arange(len(c))
    style(ax, grid_axis='x')
    for i, (_, r) in enumerate(c.iterrows()):
        if pd.notna(r['yellow']):
            ax.plot([r['yellow'], r['red']], [i, i], color=BORDER, linewidth=1.5, zorder=1)
    off = np.where((c['red'] - c['yellow']).abs() < 0.03, 0.18, 0.0)      # equal values: show both dots
    ax.scatter(c['red'], y + off, s=46, color=RED, zorder=3, edgecolors=SURFACE, linewidths=1.5, label='red alert')
    ax.scatter(c['yellow'], y - off, s=46, color=YELLOW, zorder=3, edgecolors=SURFACE, linewidths=1.5,
               label='yellow alert')
    ax.set_yticks(y)
    ax.set_yticklabels([o.replace(' oblast', '') for o in c.index], fontsize=8.5, color=INK_2)
    ax.set_ylim(-0.7, len(c) - 0.3)
    ax.set_xlim(0, 1.04)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_title("Share of the oblast's area under alert\nwhile any of its raions is", loc='left', fontsize=10,
                 color=INK, pad=22)
    ax.legend(loc='lower left', bbox_to_anchor=(-0.02, 1.0), ncol=2, frameon=False, fontsize=8.5,
              labelcolor=INK_2, handletextpad=0.2, columnspacing=1.0, borderaxespad=0)
    for i, (_, r) in enumerate(c.iterrows()):
        hy = '-' if pd.isna(r['yellow']) else f"{r['hours_yellow']:.0f}"
        ax.text(1.09, i, f"{hy} / {r['hours_red']:.0f}", transform=ax.get_yaxis_transform(), fontsize=8,
                color=MUTED, va='center', ha='left')
    ax.text(1.09, len(c) - 0.2, 'hours under\nalert, Y / R', transform=ax.get_yaxis_transform(), fontsize=8,
            color=INK_2, va='bottom', ha='left')
    fig.text(0.70, 0.012, 'Time-weighted over the minutes with an alert of that level. Kyiv City is one unit; '
             'Zakarpattia had no yellow alert.', fontsize=8, color=INK_2, ha='left', va='bottom', wrap=True)
    fig.savefig(file, dpi=150, facecolor=SURFACE)
    plt.close(fig)


# --- D07 / D23: how synchronous the raions of an oblast are ----------------------------------
def synchrony_figure(base: MapBase, units: pd.DataFrame, panels: list, file) -> None:
    """Side-by-side maps of the mean minute-level Jaccard of each raion with the other raions of its
    oblast. panels: [(title, {(oblast, raion): value}), ...]."""
    fig = plt.figure(figsize=(6.6 * len(panels), 5.9), facecolor=SURFACE)
    fig.text(0.008, 0.985, 'How often the raions of one oblast are under alert together', ha='left', va='top',
             fontsize=14, color=INK, weight='bold')
    fig.text(0.008, 0.925, 'Each raion: minute-level Jaccard with the other raions of its oblast, averaged '
             '(1 = always together). Before the alert levels the west was announced as a whole and the east and south '
             'raion by raion (D07);\nafter them the west splits too, because yellow alerts are announced per raion (D23). '
             'Zaporizhzhia stays dark: its five raions are one unit of identical series.',
             ha='left', va='top', fontsize=9.5, color=INK_2, linespacing=1.45)
    inside = np.array([u is not None for u in feature_units(base, units)])
    w = 1 / len(panels)
    for k, (ttl, val) in enumerate(panels):
        ax = fig.add_axes([k * w + 0.005, 0.1, w - 0.01, 0.69])
        v = np.array([val.get(n, np.nan) for n in base.names])
        colors = [RAMP(x) if np.isfinite(x) else QUIET for x in v]
        draw(ax, base, colors, hatch_mask=~inside)
        ax.set_title(ttl, loc='left', fontsize=10, color=INK, pad=2)
        if k == 0:
            _legend(ax, [Patch(facecolor=QUIET, edgecolor=BORDER, label='one unit (Kyiv)'),
                         Patch(facecolor=OUTSIDE, edgecolor=BORDER, hatch='////', label='outside the forecast')])
    _prob_bar(fig, [0.62 if len(panels) > 1 else 0.55, 0.06, 0.3, 0.025], 'Jaccard with the other raions of the oblast', percent=False)
    fig.savefig(file, dpi=150, facecolor=SURFACE)
    plt.close(fig)


# --- the forecast on a map: one moment, or an animation --------------------------------------
@dataclass
class Frame:
    t: pd.Timestamp
    under: dict            # unit_id -> True when under alert
    prob: dict             # unit_id -> forecast probability (quiet units with a forecast)
    new: set               # unit_ids whose alert started in the last step
    no_data: set           # unit_ids without data at t (masks of the channel outage)


def frames(intervals: pd.DataFrame, masks: pd.DataFrame, preds: pd.DataFrame, unit_ids: list,
           times: pd.DatetimeIndex, step: pd.Timedelta) -> tuple[list, pd.Series]:
    """Frames at `times`: the recorded alert state (segments), episode starts in (t - step, t], the
    outage mask, and the forecast made at the top of the hour of t for the units quiet then.
    `preds`: unit_id, t (hourly), p. Also the number of units under alert per frame (timeline)."""
    x = to_sec(times)
    ep = episodes(intervals)
    out = union(masks[masks['reason'] == OUTAGE], 'unit_id') if (masks['reason'] == OUTAGE).any() else masks.iloc[:0]
    under, new, nodata = {}, {}, {}
    for u in unit_ids:
        g = intervals[intervals['unit_id'] == u].sort_values('start_utc')
        under[u] = covers(to_sec(g['start_utc']), to_sec(g['end_utc']), x)
        st = np.sort(to_sec(ep.loc[ep['unit_id'] == u, 'start_utc']))
        new[u] = count_in(st, x - int(step.total_seconds()), x) > 0
        m = out[out['unit_id'] == u].sort_values('start')
        nodata[u] = covers(to_sec(m['start']), to_sec(m['end']), x)
    by_hour = {t: dict(zip(g['unit_id'], g['p'])) for t, g in preds.groupby('t')}
    result = []
    for k, t in enumerate(times):
        result.append(Frame(t, {u: bool(under[u][k]) for u in unit_ids}, by_hour.get(t.floor('h'), {}),
                            {u for u in unit_ids if new[u][k]}, {u for u in unit_ids if nodata[u][k]}))
    timeline = pd.Series(np.sum([under[u] for u in unit_ids], axis=0), index=times)
    return result, timeline


class ForecastMap:
    """A map of the alert state and the forecast, redrawn frame by frame (animation) or once (snapshot)."""

    def __init__(self, base: MapBase, units: pd.DataFrame, horizon: int, title: str, subtitle: str,
                 timeline: pd.Series | None = None, new_label: str = 'alert just started',
                 quiet_label: str = 'quiet, next forecast on the hour'):
        self.base, self.fu = base, feature_units(base, units)
        self.inside = np.array([u is not None for u in self.fu])
        self.fig = plt.figure(figsize=(8.8, 7.0 if timeline is not None else 6.0), dpi=100, facecolor=SURFACE)
        top = 0.89 if timeline is not None else 0.87
        self.fig.text(0.015, 0.985, title, ha='left', va='top', fontsize=13, color=INK, weight='bold')
        self.fig.text(0.015, 0.948, subtitle, ha='left', va='top', fontsize=8.8, color=INK_2, linespacing=1.4)
        y0 = 0.2 if timeline is not None else 0.02
        self.ax = self.fig.add_axes([0.01, y0, 0.98, top - y0])
        self.fill = draw(self.ax, base, [QUIET] * len(base.names), hatch_mask=~self.inside)
        self.clock = self.fig.text(0.985, 0.985, '', ha='right', va='top', fontsize=12.5,
                                  color=INK, weight='bold', linespacing=1.3)
        o = base.order
        self.ring = PathCollection([base.paths[i] for i in o], facecolors='none', edgecolors=INK,
                                   linewidths=np.zeros(len(o)))
        self.ax.add_collection(self.ring)
        self.step_label = new_label
        self.legend = _legend(self.ax, [Patch(facecolor=RED, label='under alert'),
                                        Patch(facecolor='none', edgecolor=INK, linewidth=1.8, label=self.step_label),
                                        Patch(facecolor=QUIET, edgecolor=BORDER, label=quiet_label),
                                        Patch(facecolor=OUTSIDE, edgecolor=BORDER, hatch='////',
                                              label='outside the forecast / no data')],
                              bbox_to_anchor=(0.0, 0.0))
        _prob_bar(self.fig, [0.03, y0 + 0.21 if timeline is not None else 0.27, 0.25, 0.018],
                  f'quiet: chance an alert starts within {horizon} h')
        n_units = len({u for u in self.fu if u is not None})
        self.cursor = None
        if timeline is not None:
            tax = self.fig.add_axes([0.07, 0.05, 0.9, 0.12])
            style(tax)
            x = timeline.index.tz_convert(KYIV).tz_localize(None)
            tax.fill_between(x, timeline.to_numpy(), color=RED, alpha=0.25, linewidth=0)
            tax.plot(x, timeline.to_numpy(), color=RED, linewidth=1.5)
            tax.set_xlim(x[0], x[-1])
            tax.set_ylim(0, max(timeline.max() * 1.1, 1))
            tax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%d %b\n%H:%M'))
            tax.set_title(f'Units under alert (of {n_units})', loc='left', fontsize=8.5, color=INK_2, pad=2)
            self.cursor = tax.axvline(x[0], color=INK, linewidth=1.2)

    def update(self, fr: Frame) -> None:
        colors, widths = [], []
        for i in self.base.order:
            u = self.fu[i]
            if u is None or u in fr.no_data:
                colors.append(OUTSIDE if u is None else QUIET)
            elif fr.under.get(u):
                colors.append(RED)
            elif u in fr.prob:
                colors.append(RAMP(fr.prob[u]))
            else:
                colors.append(QUIET)
            widths.append(1.8 if u in fr.new else 0.0)
        self.fill.set_facecolors(colors)
        self.ring.set_linewidths(widths)
        k = fr.t.tz_convert(KYIV)
        self.clock.set_text(f'{k:%a %d %b, %H:%M} Kyiv')
        if self.cursor is not None:
            x = k.tz_localize(None)
            self.cursor.set_xdata([x, x])

    def image(self):
        from PIL import Image
        self.fig.canvas.draw()
        return Image.fromarray(np.asarray(self.fig.canvas.buffer_rgba())[..., :3])

    def save(self, file) -> None:
        self.fig.savefig(file, dpi=150, facecolor=SURFACE)

    def close(self) -> None:
        plt.close(self.fig)


def save_gif(images: list, file, frame_ms: int, hold_last_ms: int = 1500) -> None:
    """One shared palette for all frames (no flicker between frames), no dithering."""
    from PIL import Image
    strip = Image.new('RGB', (images[0].width, images[0].height * 3))
    for k, im in enumerate(images[:: max(1, len(images) // 3)][:3]):
        strip.paste(im, (0, k * images[0].height))
    pal = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    frames = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in images]
    durations = [frame_ms] * (len(frames) - 1) + [hold_last_ms]
    frames[0].save(file, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)
