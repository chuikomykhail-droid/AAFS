# Pre-registration: B3 (exponentially weighted B1) on the test part

Written **before** B3 was run on the test part. Status: post-submission analysis (the submission
deadline was 12 October 2026, 23:59 Kyiv time). The submitted `main` is not changed by this work.

## Why

The independent review (`reviews/FINAL.md`, F23) fixed in advance a baseline "B1 with exponential
weights, half-life 7 days" (here B3). On the validation part it equals LightGBM at h = 3 and 6. It
was not run on the test part when the project was submitted. The reason was the usage limit of the
working session at that moment, not rule 6 of `PLAN.md`: running a baseline fixed in advance and
publishing the result whatever it is does not break rule 6. The wording in README / D20 that blames
rule 6 is too strong.

## What is run

- B3 = B1 (unit x hour of day in Kyiv time, the same hierarchical smoothing with strength
  `baselines.prior_strength` = 5) fitted on **all** training rows with the weight
  `0.5 ** (age_days / 7)`, the age counted from the last training row.
- The half-life 7 days is the one fixed by the review. **No other half-life is run on the test part.**
- Walk-forward exactly as in the submitted backtest: for day D a fresh model is fitted on the rows with
  `t <= D - h`. Test days, rows and horizons h = 1, 3, 6 as in `reports/results.md`.
- Predictions of LightGBM, LR and B0-B2 are read from `data/predictions_h*.parquet` (not refitted).
- Paired bootstrap over whole days: `n_reps` and `seed` from `config.yaml`.
- The project's own rule picks the reference baseline by the lowest log loss on validation. B3 has
  the lower validation log loss at every h (0.2810 / 0.3810 / 0.3835 against B1 0.2868 / 0.3948 /
  0.4055), so the main comparison is **LightGBM - B3**.

## Predictions (written before running)

Naive additive extrapolation: the shift "B3 - B1" measured on validation is added to the submitted
test difference "LightGBM - B1".

| h | LightGBM - B1, test (README) | B3 - B1, validation | Expected LightGBM - B3: PR-AUC / log loss |
|---|---|---|---|
| 1 | +0.036 / -0.022 | +0.0005 / -0.0058 | about +0.035 / -0.016 |
| 3 | +0.027 / -0.021 | +0.0069 / -0.0138 | about +0.020 / -0.007 |
| 6 | +0.018 / -0.019 | +0.0080 / -0.0220 | about +0.010 / +0.003 |

Qualitative expectation: the advantage over B3 holds at h = 1; at h = 3 it shrinks and its interval
touches zero; at h = 6 it is not distinguishable from zero and B3 may be better by log loss.

## How the result will be read (fixed now)

- "Advantage shown" at a horizon only if the 95% interval of the paired difference LightGBM - B3
  excludes zero for PR-AUC **and** for log loss (in favour of LightGBM). Otherwise "not shown".
- One secondary analysis: LightGBM - B3 at h = 3 on the ordinary days of the test part, 2026-08-10 to
  2026-08-26 (the split of F25). No other splits.
- Every horizon and every result is published, whatever it is.

## Checks that must pass before the numbers are read

1. The project's B1 refitted by the same script equals `p_B1` in the saved predictions bit for bit.
2. Test rows are 46,574 / 46,270 / 45,767 for h = 1 / 3 / 6.
3. With reference B1 the bootstrap reproduces README: LightGBM - B1 PR-AUC = +0.036 / +0.027 / +0.018.
4. On validation B3 reproduces the review's PR-AUC 0.4129 / 0.6969 / 0.8402.

## Not touched

`config.yaml`, `src/`, `scripts/run_all.py`, the reference numbers, README, DECISIONS, PLAN, the
reports of the main run, `ai_logs/`.
