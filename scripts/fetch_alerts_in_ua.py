"""Download alert history from the alerts.in.ua API as is (PLAN 8.1, D22).

    python scripts/fetch_alerts_in_ua.py --uids 22         # one oblast first: look at location_type
    python scripts/fetch_alerts_in_ua.py --all-oblasts     # the 27 oblast uids, about 14 minutes

The token is read from the environment variable named in config.api.token_env, or else from the
git-ignored file config.api.token_file. It is sent only in the Authorization header and is never
printed or written anywhere. Responses are saved unchanged to
data/raw/alerts_in_ua/<uid>_<request time UTC>.json (git-ignored: publication terms are not
defined); a manifest line per request records status, size and the Last-Modified header.

Rate limits (devs.alerts.in.ua): history endpoints 2 requests per minute; systematic violations
block the IP and the token. Hence a pause of config.api.pause_seconds between requests, a stop on
401/403, and at most one retry after 429.
"""
import argparse
import json
import logging
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from alerts.config import ROOT, load_config  # noqa: E402

logger = logging.getLogger('fetch_alerts_in_ua')


class Stop(Exception):
    """An answer after which no further request may be sent (bad token, blocked IP)."""


def read_token(api: dict) -> str:
    token = os.environ.get(api['token_env'], '').strip()
    if not token:
        p = ROOT / api['token_file']
        token = p.read_text(encoding='utf-8').strip() if p.exists() else ''
    if not token:
        raise Stop(f"no token: set {api['token_env']} or put it into {api['token_file']}")
    return token


def get(url: str, token: str, if_modified_since: str | None = None) -> tuple[int, bytes, dict]:
    headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json',
               'User-Agent': 'AAFS research script (one-off history download)'}
    if if_modified_since:
        headers['If-Modified-Since'] = if_modified_since
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:              # the message never contains the token
        return e.code, e.read(), dict(e.headers)


def fetch(uids: list, cfg: dict) -> list[dict]:
    api = cfg['api']
    token = read_token(api)
    out_dir = ROOT / api['raw_dir']
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = out_dir / 'manifest.jsonl'
    results = []
    for i, uid in enumerate(uids):
        if i:
            time.sleep(api['pause_seconds'])
        url = api['base_url'] + api['history_path'].format(uid=uid)
        for attempt in (1, 2):
            requested = datetime.now(timezone.utc)
            status, body, headers = get(url, token)
            if status != 429 or attempt == 2:
                break
            logger.warning(f'uid {uid}: 429, waiting {api["retry_after_429_seconds"]} s before one retry')
            time.sleep(api['retry_after_429_seconds'])
        stamp = requested.strftime('%Y%m%dT%H%M%SZ')
        rec = {'uid': uid, 'status': status, 'requested_utc': requested.isoformat(), 'bytes': len(body),
               'last_modified': headers.get('Last-Modified'), 'file': None}
        if status == 200:
            f = out_dir / f'{uid}_{stamp}.json'
            f.write_bytes(body)
            rec['file'] = f.name
            try:
                rec['alerts'] = len(json.loads(body).get('alerts', []))
            except ValueError:
                rec['alerts'] = None
                logger.error(f'uid {uid}: 200 but the body is not JSON')
        else:
            rec['message'] = body[:300].decode('utf-8', errors='replace')
        with open(manifest, 'a', encoding='utf-8') as m:
            m.write(json.dumps(rec, ensure_ascii=False) + '\n')
        logger.info(f"uid {uid}: {status}, {len(body):,} bytes, alerts {rec.get('alerts')}")
        results.append(rec)
        if status in (401, 403):
            raise Stop(f'uid {uid}: HTTP {status} {rec["message"]!r}; stopping to avoid a block')
        if status == 429:
            raise Stop(f'uid {uid}: still 429 after waiting; stopping')
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--uids', nargs='+', help='location uids to download')
    g.add_argument('--all-oblasts', action='store_true', help='the oblast uids from config.api.oblast_uids')
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    cfg = load_config()
    uids = [str(u) for u in (cfg['api']['oblast_uids'] if args.all_oblasts else args.uids)]
    logger.info(f'{len(uids)} uid(s), about {len(uids) * cfg["api"]["pause_seconds"] / 60:.0f} min')
    try:
        fetch(uids, cfg)
    except Stop as e:
        logger.error(str(e))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
