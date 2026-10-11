"""End-to-end build: tables of stages 1b-3, features (stage 5), backtests (stages 4, 6).

Computation only; saving is a separate step (save_all) and is done by scripts/run_all.py.
"""
import logging
from dataclasses import dataclass

import pandas as pd

from alerts import store
from alerts.config import ROOT
from alerts.features import FeatureBuilder
from alerts.geo import neighbours
from alerts.grid import build_grid
from alerts.ingest.vadimkin import load_official
from alerts.intervals import build_intervals, build_seen
from alerts.mask import build_masks
from alerts.scope import select_scope
from alerts.units import build_units

logger = logging.getLogger(__name__)


@dataclass
class Artifacts:
    df: pd.DataFrame          # whole cleaned file (D03)
    scope_all: pd.DataFrame   # scope records of all time (mask rule (b) needs neighbours)
    scope: pd.DataFrame       # scope records overlapping [work_start, data_end)
    units: pd.DataFrame
    neighbors: pd.DataFrame   # unit and oblast neighbours from the boundaries (D19)
    pairs: pd.DataFrame       # Jaccard of every same-oblast pair (train period)
    masks: pd.DataFrame
    outages: pd.DataFrame
    mask_stats: dict
    intervals: pd.DataFrame
    seen: pd.DataFrame        # as-of state seen in real time (D16, D19)
    grid: pd.DataFrame        # stage 3: (unit, t) rows with targets
    grid_stats: dict


def build_all(cfg: dict) -> Artifacts:
    df = load_official(ROOT / cfg['dataset']['path'], cfg['dataset']['sha256'])
    return build_tables(df, cfg)


def build_tables(df: pd.DataFrame, cfg: dict, units: pd.DataFrame | None = None,
                 neighbors: pd.DataFrame | None = None) -> Artifacts:
    """All tables from cleaned records. `units` and `neighbors` can be given (tests)."""
    scope_all = select_scope(df, cfg, period=False)
    scope = select_scope(df, cfg, period=True)
    logger.info(f'Scope records: {len(scope_all):,} of all time, {len(scope):,} overlap the working period')

    pairs = pd.DataFrame(columns=['oblast', 'raion1', 'raion2', 'jaccard'])
    if units is None:
        units, pairs = build_units(scope, cfg)
    if neighbors is None:
        neighbors = neighbours(units, cfg)
    masks, outages, mask_stats = build_masks(df, scope_all, units, cfg)
    for o in outages.itertuples():
        logger.warning(f'Channel outage (D15): {o.start} -> {o.end} ({o.end - o.start})')
    intervals = build_intervals(scope, units, masks, cfg)
    seen = build_seen(scope, units, cfg)
    grid, grid_stats = build_grid(seen, intervals, masks, units, cfg)
    logger.info(f'Grid: {len(grid):,} rows')
    return Artifacts(df, scope_all, scope, units, neighbors, pairs, masks, outages, mask_stats, intervals, seen, grid, grid_stats)


def model_data(art: Artifacts, cfg: dict) -> pd.DataFrame:
    """Grid rows with their features: the frame every model and baseline is fitted on.

    Rows whose last 24 hours overlap a channel outage are dropped (`lookback_ok`, D19).
    """
    fb = FeatureBuilder(art.seen, art.intervals, art.units, art.masks, art.neighbors, cfg)
    data = pd.concat([art.grid, fb.build(art.grid)], axis=1)
    logger.info(f'Model data: {int(data["lookback_ok"].sum()):,} of {len(data):,} grid rows have a complete look-back')
    return data[data['lookback_ok']].drop(columns='lookback_ok')


def save_all(art: Artifacts, cfg: dict) -> None:
    store.save(art.units, cfg, 'units')
    store.save(art.masks, cfg, 'mask')
    store.save(art.intervals, cfg, 'intervals')
    store.save(art.seen, cfg, 'seen')
    store.save(art.neighbors, cfg, 'neighbors')
    store.save_parquet(art.grid, cfg, 'grid')
    report_pairs = art.pairs[art.pairs['jaccard'] >= cfg['thresholds']['similar_pairs_report']]
    store.save(report_pairs, cfg, 'similar_pairs')
