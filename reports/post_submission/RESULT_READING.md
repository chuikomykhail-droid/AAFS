# B3 on the test part: what the result says and what it does not

Numbers: `b3_test.md` / `b3_test.json`. Protocol, predictions and reading rules: `PREREGISTRATION.md`
(committed first, 75c7168). The submitted `main` is unchanged.

## Outcome against the pre-registration

All 12 checks passed (the project's B1 refitted by the script equals the saved one bit for bit;
README's LightGBM - B1 reproduced; the review's validation numbers for B3 reproduced).

| h | LightGBM - B3, PR-AUC | LightGBM - B3, log loss | Predicted PR-AUC / log loss | Shown (pre-registered rule) |
|---|---|---|---|---|
| 1 | +0.0321 [+0.0189, +0.0437] | -0.0167 [-0.0238, -0.0108] | +0.035 / -0.016 | yes |
| 3 | +0.0247 [+0.0087, +0.0370] | -0.0165 [-0.0260, -0.0066] | +0.020 / -0.007 | yes |
| 6 | +0.0175 [+0.0074, +0.0278] | -0.0146 [-0.0247, -0.0053] | +0.010 / +0.003 | yes |

**The prediction was wrong where it mattered.** I expected the advantage to shrink at h = 3, touch zero
there, and be indistinguishable from zero (even reversed by log loss) at h = 6. It did not. The
advantage over B3 is significant by both PR-AUC and log loss at every horizon.

Why the prediction failed: it assumed that B3's gain over B1 on validation carries over to the test.
It did not. B3 - B1 on validation was +0.0005 / +0.0069 / +0.0080 PR-AUC; on the test it is
+0.0041 / +0.0024 / +0.0005, all intervals include zero (log loss: -0.0055 and -0.0047 are significant
at h = 1 and 3, -0.0039 at h = 6 is not). So the stronger baseline helped much less on the test than
on validation. I did not investigate the cause; "validation was one 28-day period" is a
hypothesis, not a finding.

## What this closes

The specific doubt "an unrun baseline fixed in advance might erase the edge" is answered for this
baseline: it does not. The README sentence that part of the edge "may be memory of recent alerts"
is not supported on the test by B3 (half-life 7 days).

## What this does not close

- **Other robustness checks of the review were not repeated against B3** (not pre-registered): 7-day
  block bootstrap, the correction for multiple comparisons (F24), the API check (F43). The h = 6 doubt
  from those checks stands as it was.
- **One half-life only.** B3 is one member of the "short memory" family. U_7 (unit rate over 7 days,
  no hour of day) was close to LightGBM by log loss on validation at h = 3 and 6 and was not run on
  the test.
- **Validation still shows a tie** between B3 and LightGBM at h = 3 and 6 (LightGBM's validation
  numbers are optimistic: its hyperparameters were chosen on that period). The test disagrees. Both
  facts stand; one period of 24 days each.
- **LR is still not shown** to beat B3 at h = 3 and 6 (PR-AUC intervals include zero).
- Inside one unit the model's ROC-AUC over time is about 0.60 (F26). Untouched by this analysis.

## The one secondary analysis (ordinary days, h = 3, 2026-08-10 to 08-26, 17 days)

LightGBM - B3: PR-AUC +0.0126 [+0.0008, +0.0231], log loss -0.0090 [-0.0174, -0.0008]. Against B1 the
same split gave +0.010 [-0.002, +0.020] (F25). On these days B1 is slightly better than B3 (B1 - B3 =
+0.0028 PR-AUC, not significant), so a short memory does not help on calm days. The lower bound is
+0.0008, so I read this as "not contradicted", not as a finding.

## Wording to fix when (and if) this is merged after the interview

1. README "Results" and D20: the reason for not running B3 was the usage limit of the working
   session on 12 October, not rule 6. A baseline fixed in advance whose result is published whatever
   it is does not break rule 6.
2. Add the B3 result above; the sentence about "memory of recent alerts" needs the test result next to it.
3. "Beats the best baseline at every horizon" is then true for four baselines, with the caveats above.
4. Error log: add the entry about the pre-registered baseline that was left unrun, and about the wrong
   rationale in README / D20.
