"""Units and clone merging (D05, D06, D07). Pure functions: nothing is written to disk here."""
import logging

import numpy as np
import pandas as pd

from alerts.config import ts
from alerts.scope import LOC_KEY, ROLE_INPUT, ROLE_TARGET
from alerts.timeutil import to_sec

logger = logging.getLogger(__name__)


def build_units(scope: pd.DataFrame, cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Map every location to a unit.

    Target locations: Jaccard similarity of 1-minute "under alert" series on the train period
    within each oblast; connected components over edges >= clone_jaccard become one unit (D07).
    Input-only oblasts (D06): one unit per oblast, `I00`, `I01`, ...

    Returns (units, pairs): units has columns oblast, raion, unit_id, unit_name, role;
    pairs holds the Jaccard similarity of every same-oblast pair of target locations.
    """
    target = scope[scope['role'] == ROLE_TARGET]
    locs = target[LOC_KEY].drop_duplicates().sort_values(LOC_KEY).reset_index(drop=True)
    logger.info(f'Target locations (raions + Kyiv): {len(locs)}')

    grid = _minute_grid(target, locs, ts(cfg['periods']['work_start']), ts(cfg['periods']['train_end']))
    pairs = _pair_similarity(grid, locs)

    edges = pairs.loc[pairs['jaccard'] >= cfg['thresholds']['clone_jaccard'], ['i', 'j']].to_numpy()
    comp = _components(len(locs), edges)

    # Stable ids: components ordered by their alphabetically first raion
    members = pd.DataFrame({'comp': comp, 'raion': locs['raion'], 'oblast': locs['oblast']})
    first = members.sort_values(['raion', 'oblast']).groupby('comp')['raion'].first()
    order = first.sort_values(kind='stable').index
    comp_to_id = {c: f'U{i:03d}' for i, c in enumerate(order)}
    names = members.sort_values('raion').groupby('comp')['raion'].agg(' + '.join)

    units = locs.assign(unit_id=[comp_to_id[c] for c in comp],
                        unit_name=[names[c] for c in comp],
                        role=ROLE_TARGET)
    logger.info(f'Target units after clone merging: {units["unit_id"].nunique()}')

    inputs = scope.loc[scope['role'] == ROLE_INPUT, LOC_KEY].drop_duplicates().sort_values(LOC_KEY)
    input_ids = {ob: f'I{i:02d}' for i, ob in enumerate(sorted(inputs['oblast'].unique()))}
    inputs = inputs.assign(unit_id=inputs['oblast'].map(input_ids), unit_name=inputs['oblast'], role=ROLE_INPUT)

    units = pd.concat([units, inputs], ignore_index=True)
    pairs = pairs.drop(columns=['i', 'j']).sort_values('jaccard', ascending=False, kind='stable')
    return units, pairs.reset_index(drop=True)


def _minute_grid(records: pd.DataFrame, locs: pd.DataFrame, t0: pd.Timestamp, t1: pd.Timestamp) -> np.ndarray:
    """Boolean [location, minute] matrix of "under alert" on [t0, t1).

    Minute indices are floor((t - t0) / 60) for both ends, as in the original D07 computation.
    Built with a +1/-1 difference array and a cumulative sum instead of per-record slicing.
    """
    n_min = int((t1 - t0) // pd.Timedelta(minutes=1))
    rec = records[(records['started_at'] < t1) & (records['finished_at'] > t0)]
    loc_idx = rec[LOC_KEY].merge(locs.reset_index(), on=LOC_KEY, how='left')['index'].to_numpy()
    base = to_sec(t0)
    start_m = np.clip((to_sec(rec['started_at']) - base) // 60, 0, n_min)
    end_m = np.clip((to_sec(rec['finished_at']) - base) // 60, 0, n_min)
    keep = start_m < end_m

    grid = np.zeros((len(locs), n_min), dtype=bool)
    for i in range(len(locs)):
        sel = keep & (loc_idx == i)
        diff = np.zeros(n_min + 1, dtype=np.int32)
        np.add.at(diff, start_m[sel], 1)
        np.add.at(diff, end_m[sel], -1)
        grid[i] = np.cumsum(diff[:-1]) > 0
    return grid


def _pair_similarity(grid: np.ndarray, locs: pd.DataFrame) -> pd.DataFrame:
    """Jaccard of every same-oblast pair: |A & B| / |A | B| via one matrix product per oblast.

    float32 sums are exact here: minute counts stay far below 2**24. A pair with an empty union
    gets 0, never 1: two silent locations are not evidence of being clones.
    """
    rows = []
    for oblast, idx in locs.groupby('oblast').groups.items():
        idx = np.asarray(idx)
        x = grid[idx].astype(np.float32)
        inter = (x @ x.T).astype(np.float64)
        size = np.diag(inter)
        uni = size[:, None] + size[None, :] - inter
        jac = np.divide(inter, uni, out=np.zeros_like(inter), where=uni > 0)
        a, b = np.triu_indices(len(idx), k=1)
        rows.append(pd.DataFrame({'oblast': oblast,
                                  'raion1': locs['raion'].to_numpy()[idx[a]],
                                  'raion2': locs['raion'].to_numpy()[idx[b]],
                                  'jaccard': jac[a, b], 'i': idx[a], 'j': idx[b]}))
    return pd.concat(rows, ignore_index=True)


def _components(n: int, edges: np.ndarray) -> np.ndarray:
    """Connected component label per node (union-find)."""
    parent = np.arange(n)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)
    return np.array([find(i) for i in range(n)])
