# AAFS — forecasting air-raid alerts by raion in Ukraine

Every hour, for each raion of Ukraine where it is quiet at that moment, the model gives the probability
that an air-raid alert starts there within the next 1, 3 or 6 hours. It is tested on the last four weeks
of the newest raion-level data, retrained daily, and checked for leakage from the future on every run.

## What sets this project apart

- **The unit is a raion, not an oblast, and the data show why.** While any raion of an oblast is under
  alert, on average only about half of the oblast's area is: 52% for a yellow alert and 58% for a red one
  (D23). The project forecasts 104 units: 110 raions in 22 oblasts plus Kyiv, with raions whose series
  are practically identical merged (D05, D07).
- **The newest data, and the reason they end where they do.** The dataset's own README says it is updated
  daily, but its official series (`official_data_en.csv`) has not changed since 8 September 2026: the
  Telegram channel behind it went silent on 7 September. This was verified by the commit history, the ID of the last processed post
  and the channel itself (D02). The test is the last four weeks before that. Then the frozen model was
  checked one month later on a different source, the alerts.in.ua API, downloaded on 12 October 2026 (D22).
- **The yellow / red alert levels introduced in September 2026 are taken into account.** Cabinet of
  Ministers resolution No. 1092 of 4 September 2026 split alerts into yellow (drone threat) and red
  (missile or combined attack). All 16,710 records of the API month carry the level, and the API window
  falls almost entirely into the new regime: in 21 of 24 regions the first yellow alert comes within its
  first day. The effect was measured, not assumed (D23):
  - against a baseline refitted on the new data, what is left of the frozen model's advantage comes from
    red alerts (ROC-AUC +0.019 [+0.004, +0.032]); on yellow ones the two are on par;
  - yellow alerts are announced per raion, so the west, announced almost as a whole before the levels,
    now splits into raions too.
- **No look into the future, checked twice on every run.** Features see only what an observer had seen
  by moment `t`, including records that the source wrote retroactively. Two automated leakage checks run
  on the real data in every pipeline run, and each was shown to fail on a deliberately leaking variant
  (D16, D18, D21).
- **Every decision and every caught AI error is written down:** decisions D00–D23 and 32 caught AI errors in
  [`DECISIONS.md`](DECISIONS.md), with what was found, how, and what was done about it. The section
  below lists the errors that would have changed the results.

![Alerts and the 3-hour forecast over 36 hours of the test](reports/figures/alerts_forecast.gif)

36 hours around the busiest day of the test (27 August 2026, 430 alert starts). Red raions are under
alert; the blue shade of a quiet raion is the forecast chance that an alert starts there within 3 hours.
The forecast is made at the top of every hour by a model that saw only what was known before that day
(walk-forward backtest); a black outline marks an alert that has just started. The animation is drawn
from the saved backtest predictions: `python scripts/make_visuals.py`.

**Try a moment yourself.** `python scripts/forecast.py --at "2026-08-27 01:00"` refits the model on what
was known at that moment (Kyiv time, any hour from 28 November 2025 to 7 September 2026), prints the
quiet raions from the most to the least likely, and shows what really happened in the next 3 hours.
`--h 1`, `--top 20`, `--map file.png` and `--csv file.csv` are optional; `--source api` replays the
alerts.in.ua month with the frozen model (needs your own download, see below). One moment proves
nothing: on this one all 15 most likely raions got an alert, but the model expected 16 starts and there
were 30. The honest measure is the backtest in [Results](#results).

![Forecast at one moment and what happened](reports/figures/forecast_example.png)

## AI errors that would have changed the results

The project was built with AI assistants (Claude Code, Gemini in Antigravity) following the plan in
[`PLAN.md`](PLAN.md). The full log of 32 caught errors is at the end of [`DECISIONS.md`](DECISIONS.md);
these are the ones with the largest consequences.

| What the AI got wrong | How it was caught | What would have happened |
|---|---|---|
| Missed a 4.3-day silence of the channel inside the test (29 August – 2 September); its trace, "alerts lasting 4.7 days", was written off as an artefact (error 13) | Review of stage 2: the longest gap between events in the whole file, then the dataset's commit history | 70 of 104 units would have looked quiet for four days: 7,457 test rows at h = 3 (13.4%) with almost no positives, and the base rate of the test would have dropped from 0.260 to 0.226. The gap is now masked (D15) |
| `AlertHistory`, the "leak-free" access to history, read the alert state from recorded ends. The dataset's processor writes an invented end (start + 1 h) only when the next alert starts (error 20) | A question from the author about the order of operations; the "corrupt the future" test did not catch it | At 358 hourly moments, for 3,529 unit-moment pairs, features would have said "quiet" although no all-clear had been seen yet: information written later than its timestamp (D16) |
| After that, the "corrupt the future" check was declared sufficient against feature leaks (error 23) | A question from the author about the architecture; a variant with the leak above passed the check | A whole class of leaks, records written later than their timestamps, would have stayed unchecked. A second check, "knowledge at the cut", now fails on it (D21) |
| Concluded that one month later the frozen model beats the baseline by +0.096 PR-AUC at h = 3 (error 26) | Asking why the gain was several times larger than on the main test | The baseline had gone stale, not the model improved. Against a baseline refitted on the new data the difference is +0.017 [−0.002, +0.031] (D22) |
| Three agents of stage 1 reported tens of thousands of overlapping alerts (32,945 / 18,044 / 30,294) and two of them missed that 38% of the rows are exact duplicates (errors 2, 3) | Recounting after deduplication: 0 overlaps | Every count in the project would have been inflated, from alerts per raion to the features (D03, D11) |
| Hyperparameters were tuned on validation rows whose label windows reach into the test: 181 rows at h = 3 (error 28) | Code review after stage 8 | Model selection would have seen the first hours of the test. After the fix the choice did not change (D20) |
| Matched the API's raion names by exact strings, although the two sources use different apostrophes, U+2019 and U+0027 (error 24) | The completeness check: 116 of 119 locations found | Three raions and 454 records would have silently dropped out of the check on fresh data (D22) |

## What keeps the numbers honest

- **One command rebuilds everything from scratch:** `python scripts/run_all.py` downloads the pinned
  dataset snapshot (commit `58ee75b`; the SHA-256 of the file is checked on every load), builds the
  tables, features, backtests and reports, and exits with code 1 if any number differs from the
  reference table in `DECISIONS.md` or if a leakage check fails.
- **Two leakage checks run on the real data in every run** (`reports/leakage_check.json`):
  - *corrupting the future* (D18): all records after the cut are shuffled and everything is rebuilt; the
    training rows, the features and the forecasts of all models at the cut must match bit for bit;
  - *knowledge at the cut* (D21): what the dataset held at the cut is reconstructed, including records
    written later than their timestamps; the features must match those computed on the full data.
  Both also run in the tests on synthetic data, and each fails when a leaking variant is swapped in.
- **Features cannot reach the raw tables:** they read the history only through `AlertHistory` (D21), so a
  new feature is checked automatically.
- **Decisions about the data are fixed before the metrics:** thresholds, merged raions and masks come
  from the training period; hyperparameters are chosen once on validation; nothing is tuned on the test
  (`PLAN.md`, rules 5–6). All constants live in `config.yaml`.
- **34 tests** (`python -m pytest`), including the leakage checks.

**How to read [`DECISIONS.md`](DECISIONS.md)** (in Russian): each entry D00–D23 goes "finding → decision
→ why → alternatives → status", with the numbers it rests on. Then come the reference numbers that
`run_all.py` checks and the log of AI errors. [`PLAN.md`](PLAN.md) holds the plan, the rules for the AI
assistants and the status of each stage; all reports are in [`reports/`](reports/).

## Results

Test: 2026-08-10 – 2026-09-07, retrained daily; square brackets give the 95% interval of a bootstrap
over days, differences are paired (the full table of all models is in [`reports/results.md`](reports/results.md)):

| h | Rate | B1 (unit × hour), PR-AUC | LightGBM, PR-AUC | LightGBM − B1, PR-AUC | LightGBM − B1, log loss |
|---|---|---|---|---|---|
| 1 | 0.121 | 0.398 | 0.434 | **+0.036** [+0.019, +0.050] | −0.022 [−0.033, −0.014] |
| 3 | 0.255 | 0.674 | 0.701 | **+0.027** [+0.010, +0.041] | −0.021 [−0.033, −0.009] |
| 6 | 0.360 | 0.814 | 0.832 | **+0.018** [+0.005, +0.030] | −0.019 [−0.033, −0.006] |

Logistic regression lies between B1 and LightGBM. B0 (the overall rate) and B2 (the number of oblasts
under alert) are barely better than a random forecast: in summer at least a few frontline oblasts are
always under alert, and that number stops measuring a "wave" (D18). The calibration of LR and LightGBM
is close to the diagonal (`reports/figures/calibration_h*.png`).

The models beat the best baseline, and the difference is statistically significant but modest. Most of
the gain is within oblasts: B1 rests almost entirely on the "east versus west" difference, while the
model tells moments and neighbouring raions apart. For example, on the test at h = 3 the PR-AUC in Kyiv
is 0.63 for LR versus 0.34 for B1, and in Kyiv oblast 0.55 versus 0.34 (`reports/backtest_h3.md`).

![Forecast versus fact](reports/figures/forecast_vs_fact.png)

## Why the unit is a raion

An alert rarely covers a whole oblast. While any raion of an oblast is under alert, on average about half
of the oblast's area is: 52% for a yellow (drone) alert and 58% for a red (missile) one, in the month of
alerts.in.ua data (D23). A red alert covers the whole oblast only in the west, where the month had three
nationwide red waves; in the north and the east red alerts are local too. A forecast per oblast would
call the whole oblast for an alert that half of it never gets.

![What part of an oblast an alert covers](reports/figures/levels_coverage.png)

How synchronous the raions of an oblast are depends on the region and has changed with the alert levels.
Before them, the west was announced almost as a whole (Ternopil 0.99, Ivano-Frankivsk 0.94, Lviv 0.88:
the median Jaccard of raion pairs over the training period), while the east and the south went raion by
raion (Dnipropetrovsk 0.39, Kherson 0.42, Chernihiv 0.47; D07). After the levels the west splits too,
because yellow alerts are announced per raion. Zakarpattia is the exception before the levels (0.36):
it has very few alerts.

![How often the raions of one oblast are under alert together](reports/figures/raion_synchrony.png)

## Check on fresh data: alerts.in.ua, one month later (D22, D23)

The main test ends on 7 September. The alerts.in.ua API gives the history of the last 30 days; the
download of 12 October covers 12 September – 12 October. This is a **different source**, so the data
are not glued together: the models trained on the data up to 7 September are frozen and only predict,
while the features are computed from the API data. Details are in [`reports/api_check.md`](reports/api_check.md).

- **Matching:** all 119 locations are found, one to one. Traps caught by the checks: a different
  apostrophe character in the names; Kyiv has the type "oblast" in the API; three raions were renamed.
- **The sources agree, but they are not the same.** The time zone is right (a shift of 0 h against the
  volunteer series), and the order of raions by alert frequency is kept (Spearman 0.81). But the API
  records more alerts. The volunteer series covers both periods and separates the effects: in reality
  the starts grew ×1.26, while the pair "Vadimkin → API" gives ×1.60.
- **The frozen model:**

| h | LightGBM − B1, frozen a month ago | LightGBM − B1, refitted on the API data |
|---|---|---|
| 1 | +0.104 [+0.087, +0.119] | **+0.051** [+0.029, +0.066] |
| 3 | +0.096 [+0.081, +0.106] | +0.017 [−0.002, +0.031] |
| 6 | +0.068 [+0.059, +0.075] | +0.004 [−0.010, +0.015] |

Against the frozen baseline the gain is large, but mostly because the baseline itself went stale.
Against B1 refitted daily on the API data, the model frozen a month earlier keeps a clear advantage at
h = 1, of the same order as on the main test. At h = 3 the difference is +0.017 and its interval touches
zero (the log loss is still significantly better); on the download made one day earlier it was +0.021
[+0.002, +0.036], so at h = 3 the advantage sits at the edge of significance. At h = 6 there is none.
The leakage checks on the API period pass.

**The API window falls into the two-level regime (D23).** Every API record has `alert_level`. In 21 of the
24 regions with alerts in the window (Kyiv included) the first yellow record falls within the first day of
the window (12 September). Dnipropetrovsk oblast switches at raion level around 21 September, and
Zakarpattia has no yellow alert at all. So the check one month later also covers a different alerting
regime, and the effects of the regime and of the source cannot be separated. Three quarters of the
positive rows start with a yellow alert. Against B1 refitted on the API data, what is left of the frozen
model's advantage comes from red alerts (ROC-AUC +0.019 [+0.004, +0.032]); on yellow ones the two are on
par (+0.002 [−0.010, +0.013]). Raions of one oblast are now announced together less often (median Jaccard
0.53 before, 0.42 after, mixed with the change of source): yellow alerts are announced per raion, and only
in the west do red ones cover the whole oblast (see the maps above). Details are in
[`reports/levels_check.md`](reports/levels_check.md).

To reproduce: get your own token at alerts.in.ua, put it into `alerts_api/token.txt` (the file is in
`.gitignore`) or into the variable `ALERTS_IN_UA_TOKEN`, then run `python scripts/fetch_alerts_in_ua.py --all-oblasts`
into an empty `data/raw/alerts_in_ua/` (about 14 minutes because of the limit of 2 requests per minute)
and `python scripts/api_check.py` (then `python scripts/levels_check.py` for the alert levels, D23). The
raw API responses are not in the repository: the terms of their publication are not defined.

## Data

**Why the data end on 7 September 2026 (D01, D02).** The source is the official series of
[Vadimkin/ukrainian-air-raid-sirens-dataset](https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset),
which is collected from the Telegram channel `air_alert_ua`. Daily commits to the dataset continue, but
the file `official_data_en.csv` has not changed since commit `58ee75b` (8 September): after that date
only the volunteer oblast-level data are updated.
- How this was checked: the commit history (the file is byte-identical up to 10 October); the last
  processed post (ID 338380) is the last post of the channel itself; a manual check of the channel.
- Considered and rejected: the volunteer series (oblasts only, not raions); our own parsing of the same
  channel (there are no new posts); the alerts.in.ua API, a source with different processing that cannot
  be glued to the test. It is used separately, as a check one month later (section above).
- The snapshot is pinned: commit `58ee75b`; the SHA-256 of the file is checked on every load.
- The channel went silent a day after the two-level alert system started in Kyiv. Whether the two are
  connected is a hypothesis; it has not been checked (D23).

**Preparation (D03–D15):**
- 38% of the rows of the file are exact duplicates; deduplication is the first step;
- the raion-level mode applies in all oblasts since 2025-11-07: this is the start of the working period;
- 110 raions in 22 oblasts plus Kyiv. Raions with practically identical series (list posts of the
  channel) are merged: 104 units. Donetsk oblast is only an input for features;
- alerts longer than a day and alerts with an end invented by the dataset's processor are masked as
  "status unknown" rather than truncated;
- **from 29 August to 2 September the channel was silent for 4.3 days** (found during the review, D15).
  This gap is masked; without the mask 13% of the test rows would be false "zeros".

**Changes in the alert system:**
- 7 November 2025: alerts are announced by raion in every oblast (D04). The working period starts here.
- September 2026: two alert levels (Cabinet of Ministers resolution No. 1092 of 4 September 2026). Yellow
  means a drone threat (a 30 s siren; businesses with a shelter may keep working), red means a missile or
  combined attack (a 60 s siren; work stops). Kyiv tested the system from 06:00 Kyiv time on 6 September,
  and the other oblasts switched gradually (D23). The main test ends on 7 September: only 19 of its
  46,270 rows (Kyiv, 6 September) fall after Kyiv's switch, all of them with y = 0. Without them the results
  stay the same to the third decimal.

**Split (D14):** training until 2026-07-13, validation 4 weeks, test 2026-08-10 – 2026-09-07.

## How it works

- **Target (D17):** for a unit that is quiet at moment `t`, whether an alert starts in `(t, t+h]`.
- **Backtest (D18):** for each test day the model is retrained on the rows whose labels are already known
  by that day (`t ≤ day − h`). Metrics: PR-AUC, ROC-AUC, Brier, log loss; intervals: a bootstrap over
  whole days, with paired differences between models.
- **Baselines:** B0, the overall rate; B1, the rate per "unit × hour of day" over 4 weeks; B2, the rate
  by the number of oblasts under alert.
- **Features (D19):** the history of the unit itself, its oblast, the country and the neighbours.
  Adjacency is built from the raion boundaries of the dataset snapshot, not from memory. Calendar, unit
  identity.
- **Models (D20):** logistic regression and LightGBM. Hyperparameters, including the weight of recent
  data, are chosen once on validation.
- **History as of `t` (D16, D21):** an alert end invented by the dataset's processor is written
  retroactively, so the alert counts as open until the next start, as a real-time observer saw it.

## Limitations

- The model has not seen data for a month: the main series ended on 7 September. In a real deployment it
  would have to be retrained.
- `scripts/forecast.py` replays past moments; it is not a live forecast. A live one needs the history of
  the last week from a live source; the plan for it (a daily download of the API history plus a log of
  active alerts, and a model refitted or recalibrated on the API data) is in `PLAN.md`, "Вне MVP".
- The models were trained before the alert levels were introduced. The level is used neither as a feature
  nor as a target, because there is no labelled history before September; the target counts an alert of
  any level (D23).
- In the API data Lviv oblast has yellow alerts from 12 September, while a local news source dates the
  oblast's switch to 12 October. This discrepancy is not resolved (D23).
- Raion-level threat posts were checked on a sample of 60 posts, not on the full archive of the channel
  (D09).
- If an all-clear was lost and a new alert came within three hours, the dataset's processor silently
  replaces the first alert: such cases can be neither found nor fixed (D09).
- The masks (D10, D15) remove 15.9% of the unit-hours from the test, almost all of it the channel outage.
- Right edge: alerts not closed before the channel stopped are missing from the data (D13).
- The test has no alert at all in Lviv, Ivano-Frankivsk and Zakarpattia oblasts: the metrics for them are
  undefined.
- Before the alert levels, raions in the west were almost always announced together, so raion-level
  differentiation is weak there; in the east and the centre it really works (D07). Since the levels this
  holds only for red alerts: yellow ones are announced by raion (D23).

## Running

```
pip install -r requirements.txt
python scripts/run_all.py        # data snapshot -> tables -> features -> backtest -> reports (~30 min)
python -m pytest                 # tests
python scripts/make_visuals.py   # maps and the animation in reports/figures (~1.5 min)
python scripts/forecast.py --at "2026-08-27 01:00"   # the forecast at one moment, and what happened
```

`run_all.py` downloads the pinned dataset snapshot itself, checks all reference numbers against
`DECISIONS.md` and exits with code 1 on any mismatch or failed leakage check. The check on fresh data
needs your own alerts.in.ua token (see the section above). Old files of the early stages are in `archive/`.
