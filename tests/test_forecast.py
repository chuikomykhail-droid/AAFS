"""The embedding interface: moments, unit names and the JSON shape of a forecast."""
import json

import pandas as pd

from alerts.forecast import NO_FORECAST, QUIET, UNDER_ALERT, ForecastResult, moment, short_name


def test_moment_is_kyiv_time_rounded_down_to_the_hour():
    assert moment('2026-08-27 01:40') == pd.Timestamp('2026-08-26 22:00', tz='UTC')       # Kyiv is UTC+3 in summer
    assert moment('2026-12-01 01:40') == pd.Timestamp('2026-11-30 23:00', tz='UTC')       # UTC+2 in winter
    assert moment('2026-08-27 01:40', utc=True) == pd.Timestamp('2026-08-27 01:00', tz='UTC')
    assert moment(pd.Timestamp('2026-08-27 01:40', tz='UTC')) == pd.Timestamp('2026-08-27 01:00', tz='UTC')


def test_short_name_of_merged_units():
    assert short_name('Kyiv City') == 'Kyiv City'
    assert short_name('Berehivskyi raion + Mukachivskyi raion') == 'Berehivskyi raion + 1 more (one unit)'


def test_json_shape():
    t = pd.Timestamp('2026-08-26 22:00', tz='UTC')
    tab = pd.DataFrame({'unit_id': ['U1', 'U2', 'U3'], 'unit': ['a', 'b', 'c'], 'oblast': ['X', 'X', 'Y'],
                        'status': [QUIET, UNDER_ALERT, NO_FORECAST], 'p': [0.61234, None, None],
                        'p_b1': [0.5, None, None],
                        'alert_started': [pd.Timestamp('2026-08-26 23:02:13', tz='UTC'), pd.NaT, pd.NaT]})
    d = json.loads(ForecastResult(t, 3, 'vadimkin', 'fitted on ...', True, tab).to_json())
    assert d['moment_kyiv'] == '2026-08-27T01:00:00+03:00' and d['horizon_h'] == 3 and d['outcome_known']
    assert d['units'][0] == {'unit_id': 'U1', 'unit': 'a', 'oblast': 'X', 'status': 'quiet', 'p': 0.6123,
                             'p_b1': 0.5, 'alert_started_utc': '2026-08-26T23:02:13+00:00'}
    assert d['units'][1]['p'] is None and d['units'][1]['status'] == 'under_alert'
