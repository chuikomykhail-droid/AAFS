# B3 (B1 with exponential weights, half-life 7 days) on the test part

Post-submission analysis. Protocol and predictions were committed before this ran: `PREREGISTRATION.md`. B3 is the reference baseline by the project's own rule (lowest log loss on validation). Nothing here changes the submitted results.

## Checks

- PASS h=1 1. project B1 refitted == saved p_B1: max |diff| = 0.00e+00
- PASS h=1 2. test rows and days: 46,574 rows, 24 days
- PASS h=1 3. LightGBM - B1 reproduces README (PR-AUC): +0.036 vs README +0.036
- PASS h=1 4. B3 on validation reproduces the review (PR-AUC): 0.4129 vs review 0.4129
- PASS h=3 1. project B1 refitted == saved p_B1: max |diff| = 0.00e+00
- PASS h=3 2. test rows and days: 46,270 rows, 24 days
- PASS h=3 3. LightGBM - B1 reproduces README (PR-AUC): +0.027 vs README +0.027
- PASS h=3 4. B3 on validation reproduces the review (PR-AUC): 0.6969 vs review 0.6969
- PASS h=6 1. project B1 refitted == saved p_B1: max |diff| = 0.00e+00
- PASS h=6 2. test rows and days: 45,767 rows, 23 days
- PASS h=6 3. LightGBM - B1 reproduces README (PR-AUC): +0.018 vs README +0.018
- PASS h=6 4. B3 on validation reproduces the review (PR-AUC): 0.8402 vs review 0.8402

## Predictions against facts (LightGBM - B3)

| h | Predicted PR-AUC / log loss | Observed PR-AUC | Observed log loss | Advantage shown? |
|---|---|---|---|---|
| 1 | +0.035 / -0.016 | +0.0321 [+0.0189, +0.0437] | -0.0167 [-0.0238, -0.0108] | yes |
| 3 | +0.020 / -0.007 | +0.0247 [+0.0087, +0.0370] | -0.0165 [-0.0260, -0.0066] | yes |
| 6 | +0.010 / +0.003 | +0.0175 [+0.0074, +0.0278] | -0.0146 [-0.0247, -0.0053] | yes |

"Shown" only if the 95% interval of LightGBM - B3 excludes zero for PR-AUC (above) and for log loss (below), as fixed in the pre-registration.

## h = 1

Test: 46,574 rows, 5,624 positives, 24 days. Brackets: 95% bootstrap over days.

### Metrics

| Model | pr_auc | roc_auc | brier | log_loss |
|---|---|---|---|---|
| B1 | 0.3982 [0.3817, 0.4179] | 0.8302 [0.8177, 0.8443] | 0.0882 [0.0802, 0.0977] | 0.2872 [0.2623, 0.3179] |
| B3 | 0.4023 [0.3846, 0.4222] | 0.8346 [0.8231, 0.8480] | 0.0873 [0.0796, 0.0966] | 0.2817 [0.2590, 0.3094] |
| LR | 0.4242 [0.4006, 0.4457] | 0.8587 [0.8481, 0.8682] | 0.0842 [0.0770, 0.0925] | 0.2690 [0.2497, 0.2914] |
| LGBM | 0.4344 [0.4094, 0.4576] | 0.8625 [0.8533, 0.8716] | 0.0835 [0.0765, 0.0917] | 0.2650 [0.2466, 0.2863] |

### Difference from B3 (model - B3; PR-AUC and ROC-AUC: higher is better, Brier and log loss: lower)

| Model | pr_auc | roc_auc | brier | log_loss |
|---|---|---|---|---|
| B1 | -0.0041 [-0.0088, +0.0010] | -0.0044 [-0.0082, -0.0007] | +0.0009 [+0.0004, +0.0014] | +0.0055 [+0.0023, +0.0095] |
| LR | +0.0219 [+0.0087, +0.0335] | +0.0240 [+0.0156, +0.0310] | -0.0031 [-0.0044, -0.0019] | -0.0127 [-0.0194, -0.0072] |
| LGBM | +0.0321 [+0.0189, +0.0437] | +0.0278 [+0.0191, +0.0345] | -0.0038 [-0.0053, -0.0026] | -0.0167 [-0.0238, -0.0108] |

### B3 - B1 (what the stronger baseline gains over the submitted reference)

| Model | pr_auc | roc_auc | brier | log_loss |
|---|---|---|---|---|
| B3 | +0.0041 [-0.0010, +0.0088] | +0.0044 [+0.0007, +0.0082] | -0.0009 [-0.0014, -0.0004] | -0.0055 [-0.0095, -0.0023] |

## h = 3

Test: 46,270 rows, 11,785 positives, 24 days. Brackets: 95% bootstrap over days.

### Metrics

| Model | pr_auc | roc_auc | brier | log_loss |
|---|---|---|---|---|
| B1 | 0.6737 [0.6519, 0.7015] | 0.8665 [0.8538, 0.8814] | 0.1262 [0.1170, 0.1360] | 0.3811 [0.3536, 0.4108] |
| B3 | 0.6762 [0.6521, 0.7045] | 0.8684 [0.8552, 0.8834] | 0.1251 [0.1160, 0.1347] | 0.3764 [0.3507, 0.4032] |
| LR | 0.6920 [0.6608, 0.7215] | 0.8819 [0.8692, 0.8945] | 0.1202 [0.1120, 0.1292] | 0.3673 [0.3450, 0.3910] |
| LGBM | 0.7008 [0.6747, 0.7263] | 0.8829 [0.8709, 0.8951] | 0.1190 [0.1107, 0.1277] | 0.3599 [0.3377, 0.3842] |

### Difference from B3 (model - B3; PR-AUC and ROC-AUC: higher is better, Brier and log loss: lower)

| Model | pr_auc | roc_auc | brier | log_loss |
|---|---|---|---|---|
| B1 | -0.0024 [-0.0083, +0.0030] | -0.0020 [-0.0056, +0.0014] | +0.0011 [-0.0001, +0.0023] | +0.0047 [+0.0003, +0.0100] |
| LR | +0.0159 [-0.0035, +0.0332] | +0.0135 [+0.0037, +0.0221] | -0.0049 [-0.0095, -0.0006] | -0.0091 [-0.0216, +0.0020] |
| LGBM | +0.0247 [+0.0087, +0.0370] | +0.0145 [+0.0057, +0.0217] | -0.0061 [-0.0097, -0.0023] | -0.0165 [-0.0260, -0.0066] |

### B3 - B1 (what the stronger baseline gains over the submitted reference)

| Model | pr_auc | roc_auc | brier | log_loss |
|---|---|---|---|---|
| B3 | +0.0024 [-0.0030, +0.0083] | +0.0020 [-0.0014, +0.0056] | -0.0011 [-0.0023, +0.0001] | -0.0047 [-0.0100, -0.0003] |

### Secondary: ordinary days of the test part (2026-08-10 to 2026-08-26, 17 days), difference from B3

| Model | pr_auc | roc_auc | brier | log_loss |
|---|---|---|---|---|
| B1 | +0.0028 [-0.0021, +0.0079] | +0.0004 [-0.0022, +0.0030] | +0.0005 [-0.0003, +0.0013] | +0.0018 [-0.0013, +0.0060] |
| LR | +0.0028 [-0.0091, +0.0153] | +0.0052 [-0.0011, +0.0120] | -0.0010 [-0.0043, +0.0019] | +0.0001 [-0.0098, +0.0086] |
| LGBM | +0.0126 [+0.0008, +0.0231] | +0.0077 [+0.0006, +0.0147] | -0.0029 [-0.0058, +0.0001] | -0.0090 [-0.0174, -0.0008] |

## h = 6

Test: 45,767 rows, 16,472 positives, 23 days. Brackets: 95% bootstrap over days.

### Metrics

| Model | pr_auc | roc_auc | brier | log_loss |
|---|---|---|---|---|
| B1 | 0.8137 [0.7881, 0.8408] | 0.8964 [0.8809, 0.9128] | 0.1248 [0.1147, 0.1348] | 0.3857 [0.3539, 0.4181] |
| B3 | 0.8142 [0.7865, 0.8430] | 0.8973 [0.8822, 0.9137] | 0.1240 [0.1145, 0.1338] | 0.3817 [0.3530, 0.4110] |
| LR | 0.8270 [0.7934, 0.8570] | 0.9061 [0.8900, 0.9200] | 0.1202 [0.1114, 0.1306] | 0.3768 [0.3533, 0.4044] |
| LGBM | 0.8317 [0.8047, 0.8577] | 0.9066 [0.8921, 0.9202] | 0.1187 [0.1099, 0.1277] | 0.3671 [0.3429, 0.3926] |

### Difference from B3 (model - B3; PR-AUC and ROC-AUC: higher is better, Brier and log loss: lower)

| Model | pr_auc | roc_auc | brier | log_loss |
|---|---|---|---|---|
| B1 | -0.0005 [-0.0057, +0.0053] | -0.0009 [-0.0043, +0.0027] | +0.0008 [-0.0013, +0.0028] | +0.0039 [-0.0027, +0.0111] |
| LR | +0.0128 [-0.0035, +0.0275] | +0.0089 [-0.0007, +0.0176] | -0.0038 [-0.0104, +0.0021] | -0.0050 [-0.0223, +0.0106] |
| LGBM | +0.0175 [+0.0074, +0.0278] | +0.0094 [+0.0032, +0.0152] | -0.0053 [-0.0091, -0.0018] | -0.0146 [-0.0247, -0.0053] |

### B3 - B1 (what the stronger baseline gains over the submitted reference)

| Model | pr_auc | roc_auc | brier | log_loss |
|---|---|---|---|---|
| B3 | +0.0005 [-0.0053, +0.0057] | +0.0009 [-0.0027, +0.0043] | -0.0008 [-0.0028, +0.0013] | -0.0039 [-0.0111, +0.0027] |
