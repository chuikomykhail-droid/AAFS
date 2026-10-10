"""Explicit datetime <-> integer seconds conversion (PLAN rule 11: no .astype('int64') on dates)."""
import numpy as np
import pandas as pd

EPOCH = pd.Timestamp('1970-01-01', tz='UTC')
SECOND = pd.Timedelta(seconds=1)


def to_sec(x) -> np.ndarray:
    """tz-aware datetimes (Series, Index, array, scalar) -> int64 seconds since epoch.

    Naive datetimes raise on subtraction from the tz-aware epoch, which is intended.
    """
    if isinstance(x, pd.Timestamp):
        return np.int64((x - EPOCH) // SECOND)
    return np.asarray((pd.DatetimeIndex(x) - EPOCH) // SECOND, dtype=np.int64)


def from_sec(a) -> pd.DatetimeIndex:
    """int64 seconds since epoch -> tz-aware UTC datetimes with second resolution."""
    return (EPOCH + pd.to_timedelta(np.asarray(a, dtype=np.int64), unit='s')).as_unit('s')
