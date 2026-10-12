"""Neighbourhood of units and oblasts from the raion boundaries in the dataset snapshot (D19, PLAN rule 9).

Source: dataset_repo/example/ukr_admin2.geojson (OCHA admin-2 boundaries, valid from 2025-09-01),
pinned by SHA-256. Two raions are neighbours when their boundaries share at least
geo.min_shared_vertices vertices (rounded to geo.vertex_decimals): the polygons come from one
topologically consistent dataset, so a shared border is a run of identical vertices.

Names: geo adm1 "Kharkivska" is our "Kharkivska oblast", geo "Kyiv" is "Kyiv City"; raion names
match ours without the " raion" suffix except renamed raions, mapped explicitly in geo.renames
and checked: every location of the units table must map to exactly one polygon.
"""
import itertools
import json
from collections import defaultdict

import pandas as pd

from alerts.config import ROOT
from alerts.ingest.vadimkin import file_sha256


def _our_name(adm1: str, adm2: str, renames_back: dict) -> tuple[str, str]:
    if adm1 == 'Kyiv':
        return 'Kyiv City', 'Kyiv City'
    raion = renames_back.get(adm2, f'{adm2} raion')
    return f'{adm1} oblast', raion


def boundaries(cfg: dict) -> tuple[list, list]:
    """The pinned admin-2 features and their (oblast, raion) names in our naming, in the same order."""
    g = cfg['geo']
    p = ROOT / g['path']
    if file_sha256(p) != g['sha256']:
        raise ValueError(f'SHA-256 mismatch for {p}')
    with open(p, encoding='utf-8') as f:
        features = json.load(f)['features']
    back = {geo: ours for ours, geo in g['renames'].items()}
    return features, [_our_name(ft['properties']['adm1_name'], ft['properties']['adm2_name'], back) for ft in features]


def raion_adjacency(cfg: dict) -> pd.DataFrame:
    """Pairs of neighbouring raions in our naming: columns oblast_a, raion_a, oblast_b, raion_b."""
    g = cfg['geo']
    features, names = boundaries(cfg)

    vertex_owners = defaultdict(set)
    for i, ft in enumerate(features):
        geom = ft['geometry']
        polys = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
        for ring in (r for poly in polys for r in poly):
            for x, y in ring:
                vertex_owners[(round(x, g['vertex_decimals']), round(y, g['vertex_decimals']))].add(i)
    shared = defaultdict(int)
    for owners in vertex_owners.values():
        for a, b in itertools.combinations(sorted(owners), 2):
            shared[(a, b)] += 1
    pairs = [(names[a], names[b]) for (a, b), n in shared.items() if n >= g['min_shared_vertices']]
    rows = [(*x, *y) for x, y in pairs] + [(*y, *x) for x, y in pairs]
    return pd.DataFrame(rows, columns=['oblast_a', 'raion_a', 'oblast_b', 'raion_b']).drop_duplicates()


def neighbours(units: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Neighbour pairs (both directions) of units and of oblasts: columns level, a, b."""
    adj = raion_adjacency(cfg)
    geo_locs = set(zip(adj['oblast_a'], adj['raion_a']))
    missing = [loc for loc in zip(units['oblast'], units['raion']) if loc not in geo_locs]
    if missing:
        raise ValueError(f'locations not found in the boundaries: {missing}')

    key = dict(zip(zip(units['oblast'], units['raion']), units['unit_id']))
    a = [key.get(k) for k in zip(adj['oblast_a'], adj['raion_a'])]
    b = [key.get(k) for k in zip(adj['oblast_b'], adj['raion_b'])]
    unit_pairs = pd.DataFrame({'a': a, 'b': b}).dropna()
    unit_pairs = unit_pairs[unit_pairs['a'] != unit_pairs['b']].drop_duplicates()

    ours = set(units['oblast'])
    ob = adj[(adj['oblast_a'] != adj['oblast_b']) & adj['oblast_a'].isin(ours) & adj['oblast_b'].isin(ours)]
    ob_pairs = ob[['oblast_a', 'oblast_b']].drop_duplicates().set_axis(['a', 'b'], axis=1)
    out = pd.concat([unit_pairs.assign(level='unit'), ob_pairs.assign(level='oblast')], ignore_index=True)
    return out[['level', 'a', 'b']].sort_values(['level', 'a', 'b']).reset_index(drop=True)
