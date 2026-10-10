import os
import sys
import pandas as pd
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from alerts.ingest.vadimkin import load_official

def test_load_official():
    # We will just test with the actual file if it exists, or mock it.
    path = "dataset_repo/datasets/official_data_en.csv"
    if not os.path.exists(path):
        pytest.skip("Dataset not found locally")
        
    expected_sha256 = "b396f87696243069eec0219880e87dcd642b20beb0a7bae0d0e1f61e1ed20ec4"
    df = load_official(path, expected_sha256)
    
    # 1. No duplicates
    assert len(df) == len(df.drop_duplicates()), "Dataframe contains duplicates"
    
    # 2. Timezone-aware and UTC
    assert df['started_at'].dt.tz is not None, "started_at is not timezone-aware"
    assert str(df['started_at'].dt.tz) == 'UTC', "started_at is not UTC"
    
    assert df['finished_at'].dt.tz is not None, "finished_at is not timezone-aware"
    assert str(df['finished_at'].dt.tz) == 'UTC', "finished_at is not UTC"
    
    # 3. No duration <= 0
    df['duration'] = (df['finished_at'] - df['started_at']).dt.total_seconds()
    assert (df['duration'] <= 0).sum() == 0, "Found duration <= 0"

