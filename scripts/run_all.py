"""One command from scratch: snapshot -> stages 1b-2 -> data tables, summaries, figures.

    python scripts/run_all.py

Exits with code 1 if a recomputed number differs from the DECISIONS.md reference table.
"""
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from alerts import report  # noqa: E402
from alerts.config import load_config  # noqa: E402
from alerts.pipeline import build_all, save_all  # noqa: E402
from fetch_data import ensure_snapshot  # noqa: E402


def main() -> int:
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(name)s: %(message)s')
    t0 = time.time()
    cfg = load_config()
    ensure_snapshot(cfg)
    art = build_all(cfg)
    save_all(art, cfg)
    mismatches = report.write_all(art, cfg)
    logging.info(f'Done in {time.time() - t0:.1f} s')
    return 1 if mismatches else 0


if __name__ == '__main__':
    sys.exit(main())
