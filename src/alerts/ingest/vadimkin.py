import pandas as pd
import hashlib
import logging

logger = logging.getLogger(__name__)

def load_official(path: str, expected_sha256: str) -> pd.DataFrame:
    """
    Load the official dataset from Vadimkin.
    Performs SHA-256 check, deduplication, and initial cleaning (duration > 0).
    """
    # 1. SHA-256 Check
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    file_hash = sha256_hash.hexdigest()
    if file_hash != expected_sha256:
        raise ValueError(f"SHA-256 mismatch! Expected {expected_sha256}, got {file_hash}")
    
    logger.info("SHA-256 hash verified.")
    
    # 2. Load and parse as UTC
    df = pd.read_csv(path)
    initial_rows = len(df)
    
    df['started_at'] = pd.to_datetime(df['started_at'], utc=True)
    df['finished_at'] = pd.to_datetime(df['finished_at'], utc=True)
    
    # 3. Deduplication
    df = df.drop_duplicates()
    dedup_rows = len(df)
    
    # 4. Remove negative or zero durations
    df['duration'] = (df['finished_at'] - df['started_at']).dt.total_seconds()
    df = df[df['duration'] > 0].copy()
    cleaned_rows = len(df)
    
    logger.info(f"Loaded {path}")
    logger.info(f"Rows initially: {initial_rows:,}")
    logger.info(f"Rows after drop_duplicates: {dedup_rows:,}")
    logger.info(f"Rows after dropping duration <= 0: {cleaned_rows:,}")
    
    return df

