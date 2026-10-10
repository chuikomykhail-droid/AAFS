"""Get the pinned dataset snapshot (D01): clone if missing, check out the commit, verify SHA-256."""
import logging
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from alerts.config import ROOT, load_config  # noqa: E402
from alerts.ingest.vadimkin import file_sha256  # noqa: E402

logger = logging.getLogger(__name__)


def _git(*args):
    subprocess.run(['git', *args], check=True)


def ensure_snapshot(cfg: dict) -> Path:
    ds = cfg['dataset']
    target, repo = ROOT / ds['path'], ROOT / ds['repo_dir']
    if target.exists() and file_sha256(target) == ds['sha256']:
        logger.info(f'Snapshot present and verified: {target}')
        return target

    if not (repo / '.git').exists():
        logger.info(f'Cloning {ds["repo_url"]} into {repo}')
        _git('clone', ds['repo_url'], str(repo))
    else:
        _git('-C', str(repo), 'fetch', 'origin')
    _git('-C', str(repo), 'checkout', '--quiet', ds['commit'])

    got = file_sha256(target)
    if got != ds['sha256']:
        raise ValueError(f'SHA-256 mismatch after checkout of {ds["commit"]}: {got}')
    logger.info(f'Snapshot {ds["commit"][:7]} checked out and verified')
    return target


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    ensure_snapshot(load_config())
