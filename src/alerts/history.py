"""As-of access to alert history (D16): the only way features should read intervals.

Information set at moment t: everything a real-time observer of the channel had seen by t.
An alert that started at or before t and had not been seen to end by t is active; its end is
never returned. The target uses (t, t+h], so the two never share an event.

The state is read from [start_utc, open_until), not from the recorded end:
  * an invented end start + 1 h (alerts.processor) is written only at the next start, so until
    then the alert stays open, as the observer saw it (no all-clear arrived);
  * segments are not bridged across pauses (D12), so a unit in a short pause is quiet.

What is deliberately not exposed, because it depends on the future:
  * episode ends;
  * masks of rules (a), (b) and the `uncertain` flag (known only after 24 h or at the next start).
Outages (D15) are exposed clipped at t: a silent channel is observable while it is silent.

All methods take moments T (DatetimeIndex, tz-aware) and return arrays of shape
(len(T), len(unit_ids)). Every query is a binary search, so the cost is O(len(T) * log n).
"""
import numpy as np
import pandas as pd

from alerts.mask import OUTAGE
from alerts.spans import union
from alerts.timeutil import to_sec


class AlertHistory:
    def __init__(self, intervals: pd.DataFrame, unit_ids, masks: pd.DataFrame | None = None):
        self.unit_ids = list(unit_ids)
        # Held-open segments can overlap later ones: rebuild disjoint "seen as open" intervals
        seen = union(intervals.rename(columns={'start_utc': 'start', 'open_until': 'end'})
                     [['unit_id', 'start', 'end']], 'unit_id')
        self._seg = {}
        self._ep_start = {}
        for u in self.unit_ids:
            g = seen[seen['unit_id'] == u]
            s, e = to_sec(g['start']), to_sec(g['end'])
            # cumulative duration of all intervals before interval k
            before = np.concatenate([[0], np.cumsum(e - s)[:-1]]) if len(s) else np.zeros(0, np.int64)
            self._seg[u] = (s, e, before)
            ep = intervals[intervals['unit_id'] == u]
            self._ep_start[u] = np.sort(to_sec(ep.groupby('episode')['start_utc'].min()))
        out = (masks[masks['reason'] == OUTAGE] if masks is not None else pd.DataFrame(columns=['start', 'end']))
        out = union(out.assign(k=0), 'k') if len(out) else out
        self._outage = (to_sec(out['start']), to_sec(out['end'])) if len(out) else (np.zeros(0, np.int64),) * 2

    # --- state now ---------------------------------------------------------------------------
    def active(self, T) -> np.ndarray:
        """Unit under alert at t: the last segment starting at or before t has not ended by t."""
        t = to_sec(T)

        def f(s, e, _):
            if len(s) == 0:
                return np.zeros(len(t), dtype=bool)
            k = np.searchsorted(s, t, side='right') - 1
            return (k >= 0) & (e[np.maximum(k, 0)] > t)
        return self._per_unit(f)

    def seconds_since_end(self, T) -> np.ndarray:
        """t minus the latest segment end <= t; NaN if there is none yet."""
        t = to_sec(T)

        def f(s, e, _):
            if len(e) == 0:
                return np.full(len(t), np.nan)
            k = np.searchsorted(e, t, side='right') - 1  # segments are disjoint, so ends are sorted
            return np.where(k >= 0, t - e[np.maximum(k, 0)], np.nan)
        return self._per_unit(f, dtype=float)

    # --- counts and shares over a look-back window (t - w, t] --------------------------------
    def starts(self, T, window: pd.Timedelta) -> np.ndarray:
        """Number of episode starts in (t - window, t]. Episode starts are fixed once they happen."""
        t, w = to_sec(T), int(window // pd.Timedelta(seconds=1))
        out = np.zeros((len(t), len(self.unit_ids)), dtype=np.int64)
        for j, u in enumerate(self.unit_ids):
            st = self._ep_start[u]
            out[:, j] = np.searchsorted(st, t, side='right') - np.searchsorted(st, t - w, side='right')
        return out

    def seconds_active(self, T, window: pd.Timedelta) -> np.ndarray:
        """Seconds under alert in (t - window, t], counting only what has happened by t."""
        t, w = to_sec(T), int(window // pd.Timedelta(seconds=1))
        return self._per_unit(lambda s, e, b: _covered(s, e, b, t) - _covered(s, e, b, t - w), dtype=float)

    def outage_seconds(self, T, window: pd.Timedelta) -> np.ndarray:
        """Seconds of channel outage in (t - window, t]; the same for every unit, shape (len(T),)."""
        t, w = to_sec(T), int(window // pd.Timedelta(seconds=1))
        s, e = self._outage
        before = np.concatenate([[0], np.cumsum(e - s)[:-1]]) if len(s) else np.zeros(0, np.int64)
        return (_covered(s, e, before, t) - _covered(s, e, before, t - w)).astype(float)

    # --- helpers -----------------------------------------------------------------------------
    def _per_unit(self, f, dtype=bool) -> np.ndarray:
        cols = [f(*self._seg[u]) for u in self.unit_ids]
        return np.column_stack(cols).astype(dtype) if cols else np.zeros((0, 0), dtype=dtype)


def _covered(s: np.ndarray, e: np.ndarray, before: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Seconds covered by disjoint sorted segments on (-inf, x]."""
    if len(s) == 0:
        return np.zeros(len(x), dtype=np.int64)
    k = np.searchsorted(s, x, side='right') - 1
    kk = np.maximum(k, 0)
    inside = np.minimum(x, e[kk]) - s[kk]
    return np.where(k >= 0, before[kk] + inside, 0)
