"""End-to-end build of stages 1b-2: computation only; saving is a separate step."""
import logging
from dataclasses import dataclass

import pandas as pd

from alerts import store
from alerts.config import ROOT
from alerts.ingest.vadimkin import load_official
from alerts.intervals import build_intervals
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
    pairs: pd.DataFrame       # Jaccard of every same-oblast pair (train period)
    masks: pd.DataFrame
    outages: pd.DataFrame
    mask_stats: dict
    intervals: pd.DataFrame


def build_all(cfg: dict) -> Artifacts:
    df = load_official(ROOT / cfg['dataset']['path'], cfg['dataset']['sha256'])
    scope_all = select_scope(df, cfg, period=False)
    scope = select_scope(df, cfg, period=True)
    logger.info(f'Scope records: {len(scope_all):,} of all time, {len(scope):,} overlap the working period')

    units, pairs = build_units(scope, cfg)
    masks, outages, mask_stats = build_masks(df, scope_all, units, cfg)
    for o in outages.itertuples():
        logger.warning(f'Channel outage (D15): {o.start} -> {o.end} ({o.end - o.start})')
    intervals = build_intervals(scope, units, masks, cfg)
    return Artifacts(df, scope_all, scope, units, pairs, masks, outages, mask_stats, intervals)


def save_all(art: Artifacts, cfg: dict) -> None:
    store.save(art.units, cfg, 'units')
    store.save(art.masks, cfg, 'mask')
    store.save(art.intervals, cfg, 'intervals')
    report_pairs = art.pairs[art.pairs['jaccard'] >= cfg['thresholds']['similar_pairs_report']]
    store.save(report_pairs, cfg, 'similar_pairs')
