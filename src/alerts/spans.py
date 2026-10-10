"""Vectorised interval operations shared by masks, intervals and reports."""
import numpy as np
import pandas as pd


def merge_labels(df: pd.DataFrame, key: str, start: str, end: str,
                 gap: pd.Timedelta = pd.Timedelta(0)) -> np.ndarray:
    """Group ids for rows of `df` sorted by (key, start).

    A row joins the current group of its key if it starts no later than `gap` after the
    running maximum end of that group. gap=0 is a union of overlapping or touching intervals;
    gap>0 also bridges short pauses. Equivalent to the classic sort-and-extend loop.
    """
    if df.empty:
        return np.zeros(0, dtype=np.int64)
    d = df[[key, start, end]].reset_index(drop=True)  # positional alignment, index may repeat
    running_end = d.groupby(key, sort=False)[end].cummax()
    prev_end = running_end.groupby(d[key], sort=False).shift(1)
    new_group = prev_end.isna() | ((d[start] - prev_end) > gap)
    return new_group.to_numpy().cumsum() - 1


def union(df: pd.DataFrame, key: str, start: str = 'start', end: str = 'end',
          gap: pd.Timedelta = pd.Timedelta(0)) -> pd.DataFrame:
    """Disjoint union of intervals per key, columns [key, start, end]."""
    df = df.sort_values([key, start, end])
    labels = merge_labels(df, key, start, end, gap)
    return (df.groupby(labels)
              .agg(**{key: (key, 'first'), start: (start, 'min'), end: (end, 'max')})
              .reset_index(drop=True))


def clipped_seconds(start: pd.Series, end: pd.Series, lo: pd.Timestamp, hi: pd.Timestamp) -> float:
    """Total seconds of [start, end) intervals inside [lo, hi). Intervals must be disjoint per key."""
    s = start.where(start > lo, lo)
    e = end.where(end < hi, hi)
    return float(((e - s).dt.total_seconds()).clip(lower=0).sum())


def overlaps(rec_start: np.ndarray, rec_end: np.ndarray,
             m_start: np.ndarray, m_end: np.ndarray) -> np.ndarray:
    """For each record [rec_start, rec_end), does it overlap any of the disjoint sorted intervals?

    Arrays are int64 seconds. Only the last interval starting before the record end can overlap,
    because the intervals are disjoint and sorted.
    """
    if len(m_start) == 0:
        return np.zeros(len(rec_start), dtype=bool)
    k = np.searchsorted(m_start, rec_end, side='left') - 1
    ok = k >= 0
    return ok & (m_end[np.maximum(k, 0)] > rec_start)
