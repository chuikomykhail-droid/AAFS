"""Artifacts of the official channel processor (D09, D10, D16).

What the processor does for one source location (dataset_repo/processors/official_channel_processor.py):
  * "Повітряна тривога" opens an alert in memory; nothing is written yet;
  * "Відбій" closes it and writes the record with the real end;
  * a new alert while one is still open (its all-clear was lost):
      - more than 3 h after the open start: the open alert is written with end = start + 1 h,
        and this invented end appears in the CSV only now, at the new start;
      - within 3 h: the open alert is replaced, its start disappears from the CSV without a trace.

So an invented end carries the timestamp start + 1 h but becomes known only at the next start.
"""
import pandas as pd


def flag_records(records: pd.DataFrame, cfg: dict, key: list[str]) -> pd.DataFrame:
    """Add per-record columns, computed over all records of the same source location `key`.

    next_start   start of the next record of the location (NaT for the last one);
    is_long      rule (a): longer than long_alert_hours;
    is_fake_end  rule (b): exactly fake_end_duration_s and the next start more than
                 fake_end_next_start_h later. Retrospective: it needs the next start, so it is
                 for masks (target side) only;
    open_until   until when the alert looked open to a real-time observer (D16). A record of
                 exactly fake_end_duration_s is treated as never closed by an all-clear and stays
                 open until the next start of its location. Decided from the record itself, not
                 from the 3-hour test, because that test needs the future.
    """
    rec = records.sort_values(key + ['started_at'])
    rec['next_start'] = rec.groupby(key, sort=False)['started_at'].shift(-1)

    fake_s = cfg['processor']['fake_end_duration_s']
    fake_gap = pd.Timedelta(hours=cfg['processor']['fake_end_next_start_h'])
    rec['is_long'] = rec['duration'] > cfg['thresholds']['long_alert_hours'] * 3600
    invented_length = rec['duration'] == fake_s
    rec['is_fake_end'] = invented_length & ((rec['next_start'] - rec['started_at']) > fake_gap)

    later_start = rec['next_start'].where(rec['next_start'] > rec['finished_at'])
    rec['open_until'] = rec['finished_at'].where(~invented_length | later_start.isna(), later_start)
    return rec.sort_index()
