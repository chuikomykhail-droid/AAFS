import hashlib
import logging

import pandas as pd

logger = logging.getLogger(__name__)


def file_sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def load_official(path, expected_sha256: str) -> pd.DataFrame:
    """Load the official Vadimkin dataset (D01, D03).

    SHA-256 check, UTC parsing, drop_duplicates, then drop durations <= 0.
    Row counts of every step are logged and kept in df.attrs['row_counts'].
    """
    file_hash = file_sha256(path)
    if file_hash != expected_sha256:
        raise ValueError(f'SHA-256 mismatch! Expected {expected_sha256}, got {file_hash}')
    logger.info('SHA-256 hash verified.')

    df = pd.read_csv(path)
    initial_rows = len(df)

    df['started_at'] = pd.to_datetime(df['started_at'], utc=True).dt.as_unit('s')
    df['finished_at'] = pd.to_datetime(df['finished_at'], utc=True).dt.as_unit('s')

    df = df.drop_duplicates()
    dedup_rows = len(df)

    df['duration'] = (df['finished_at'] - df['started_at']).dt.total_seconds()
    df = df[df['duration'] > 0].reset_index(drop=True)
    cleaned_rows = len(df)

    logger.info(f'Loaded {path}')
    logger.info(f'Rows initially: {initial_rows:,}')
    logger.info(f'Rows after drop_duplicates: {dedup_rows:,}')
    logger.info(f'Rows after dropping duration <= 0: {cleaned_rows:,}')

    df.attrs['row_counts'] = {'raw': initial_rows, 'dedup': dedup_rows, 'cleaned': cleaned_rows}
    return df
