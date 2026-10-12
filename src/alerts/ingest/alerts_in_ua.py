"""alerts.in.ua history -> records in the schema of load_official (PLAN stage 8, D22).

Raw responses (scripts/fetch_alerts_in_ua.py) are merged by `id`; when an alert was downloaded more
than once, the version with the later `updated_at` wins. Only `air_raid` alerts are kept.
Locations are matched by their Ukrainian names through data/alerts_in_ua_locations.csv
(build_locations): Vadimkin publishes the same records in English and in Ukrainian row by row, so
the English keys of our units get their Ukrainian names from official_data_uk.csv; raions renamed
in 2023-2024 take the new name from the boundaries (geo.renames + adm2_name1).

Levels: `raion` records map to raions; Kyiv city (`м. Київ`) maps to the Kyiv City unit whatever
its location_type; `oblast` records are expanded to every raion of the oblast; `city` and `hromada`
records are dropped, as hromadas in D08. An alert still open at download time (finished_at = null)
ends at the request time of its file, which lies after data_end of this source.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from alerts.config import ROOT
from alerts.ingest.vadimkin import file_sha256

KYIV_UK = 'м. Київ'
# Vadimkin writes the apostrophe as U+2019, the API as U+0027 ("Кам'янський район"): match on a normal form
APOSTROPHES = str.maketrans({c: "'" for c in '’ʼ‘`′'})
COLUMNS = ['oblast', 'raion', 'hromada', 'level', 'started_at', 'finished_at', 'duration', 'source']


def norm(name: pd.Series) -> pd.Series:
    return name.str.translate(APOSTROPHES).str.strip()


def _utc(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, utc=True, format='ISO8601').dt.floor('s').dt.as_unit('s')


def _requested(f: Path) -> pd.Timestamp:
    """Request time from a response file name <uid>_<request time UTC>.json."""
    return pd.to_datetime(f.stem.split('_', 1)[1], format='%Y%m%dT%H%M%SZ', utc=True).as_unit('s')


def downloads(raw_dir) -> pd.DataFrame:
    """Every saved response: columns uid, requested_utc. What was downloaded, unlike read_raw, which
    keeps only the file of the latest version of each alert."""
    files = sorted(Path(raw_dir).glob('*_*.json'))
    return pd.DataFrame({'uid': [f.stem.split('_', 1)[0] for f in files],
                         'requested_utc': pd.DatetimeIndex([_requested(f) for f in files], tz='UTC').as_unit('s')})


def read_raw(raw_dir) -> pd.DataFrame:
    """All downloaded alerts, one row per id (latest updated_at), with the request time of its file."""
    frames = []
    for f in sorted(Path(raw_dir).glob('*_*.json')):
        body = json.loads(f.read_text(encoding='utf-8'))
        a = pd.DataFrame(body['alerts'])
        a['requested_utc'] = _requested(f)
        a['file'] = f.name
        frames.append(a)
    if not frames:
        raise FileNotFoundError(f'no responses in {raw_dir}: run scripts/fetch_alerts_in_ua.py')
    a = pd.concat(frames, ignore_index=True)
    for c in ['started_at', 'finished_at', 'updated_at']:
        a[c] = _utc(a[c])
    a = a.sort_values(['id', 'updated_at', 'requested_utc']).drop_duplicates('id', keep='last')
    return a.reset_index(drop=True)


def build_locations(units: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Our location keys with the Ukrainian oblast and location names used by the API."""
    ds = cfg['dataset']
    for key, sha in [('path', 'sha256'), ('path_uk', 'sha256_uk')]:
        if file_sha256(ROOT / ds[key]) != ds[sha]:
            raise ValueError(f'SHA-256 mismatch for {ds[key]}')
    en = pd.read_csv(ROOT / ds['path'], usecols=['oblast', 'raion', 'level', 'started_at'])
    uk = pd.read_csv(ROOT / ds['path_uk'], usecols=['oblast', 'raion', 'level', 'started_at'])
    if len(en) != len(uk) or not (en[['level', 'started_at']].values == uk[['level', 'started_at']].values).all():
        raise ValueError('official_data_en and _uk are not aligned row by row')
    pairs = pd.DataFrame({'oblast': en['oblast'], 'raion': en['raion'].fillna(en['oblast']),
                          'oblast_uk': uk['oblast'], 'title_uk': uk['raion'].fillna(uk['oblast'])}).drop_duplicates()
    if pairs.duplicated(['oblast', 'raion']).any():
        raise ValueError('an English location has several Ukrainian names')

    loc = units[['oblast', 'raion', 'unit_id', 'role']].merge(pairs, on=['oblast', 'raion'], how='left')
    renamed = _renamed_uk(cfg)
    loc['source_of_name'] = 'official_data_uk'
    is_renamed = loc['raion'].isin(renamed)
    loc.loc[is_renamed, 'title_uk'] = loc.loc[is_renamed, 'raion'].map(renamed)
    loc.loc[is_renamed, 'source_of_name'] = 'boundaries (renamed raion)'
    keys = pd.DataFrame({'o': norm(loc['oblast_uk'].fillna('')), 'n': norm(loc['title_uk'].fillna(''))})
    if loc['title_uk'].isna().any() or keys.duplicated().any():          # one to one, also after normalising
        raise ValueError(f'locations without a unique Ukrainian name: {loc[loc["title_uk"].isna()].to_dict("records")}')
    return loc


def _renamed_uk(cfg: dict) -> dict:
    g = cfg['geo']
    with open(ROOT / g['path'], encoding='utf-8') as f:
        props = [ft['properties'] for ft in json.load(f)['features']]
    by_en = {p['adm2_name']: p['adm2_name1'] for p in props}
    return {ours: f'{by_en[geo]} район' for ours, geo in g['renames'].items()}


def load_alerts_in_ua(raw: pd.DataFrame, locations: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Records (schema of load_official, plus `api_id`) and counts of what was kept and dropped."""
    stats = {'downloaded': len(raw), 'by_alert_type': raw['alert_type'].value_counts().to_dict()}
    a = raw[raw['alert_type'] == 'air_raid'].copy()
    a['finished_at'] = a['finished_at'].fillna(a['requested_utc'])
    stats['open_at_download'] = int(raw.loc[raw['alert_type'] == 'air_raid', 'finished_at'].isna().sum())
    stats['by_location_type'] = a['location_type'].value_counts().to_dict()

    key = locations.assign(o=norm(locations['oblast_uk']), n=norm(locations['title_uk'])).set_index(['o', 'n'])
    key = key[['oblast', 'raion']]
    a['o'], a['n'] = norm(a['location_oblast']), norm(a['location_title'])
    kyiv = a['n'] == KYIV_UK
    raion = a[(a['location_type'] == 'raion') & ~kyiv]
    m = raion.join(key, on=['o', 'n'])
    unmatched = m[m['raion'].isna()].groupby(['location_oblast', 'location_title']).size()
    stats['unmatched_raions'] = {f'{o} / {t}': int(n) for (o, t), n in unmatched.items()}
    m = m[m['raion'].notna()].assign(level='raion')

    k = a[kyiv].assign(oblast='Kyiv City', raion=np.nan, level='oblast')
    ob = a[(a['location_type'] == 'oblast') & ~kyiv]
    expanded = []
    for _, r in ob.iterrows():                       # an alert for the whole oblast: every raion of it
        targets = locations[(norm(locations['oblast_uk']) == r['o']) & (locations['oblast'] != 'Kyiv City')]
        expanded.append(targets[['oblast', 'raion']].assign(started_at=r['started_at'],
                                                             finished_at=r['finished_at'], id=r['id']))
    exp = pd.concat(expanded, ignore_index=True).assign(level='raion') if expanded else pd.DataFrame()
    stats['oblast_records'] = ob.groupby('location_oblast').size().to_dict()
    stats['oblast_records_expanded'] = sum(len(x) > 0 for x in expanded)
    stats['dropped_city_hromada'] = int(a['location_type'].isin(['city', 'hromada']).sum() - kyiv.sum())

    out = pd.concat([m, k, exp], ignore_index=True)
    out = out.assign(hromada=np.nan, source='alerts_in_ua', api_id=out['id'])
    out['duration'] = (out['finished_at'] - out['started_at']).dt.total_seconds()
    stats['non_positive_duration'] = int((out['duration'] <= 0).sum())
    out = out[out['duration'] > 0]
    stats['records'] = len(out)
    return out[COLUMNS + ['api_id']].reset_index(drop=True), stats
