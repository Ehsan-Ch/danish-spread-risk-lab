# Fixed research protocol

Defined 24 October 2026 before running this project's model comparison. The source and calendar are reused from Nordcast, whose results were already inspected. This is a new fixed-model chronological replay on a familiar benchmark, **not a pristine independent or prospective holdout**.

## Targets and information

- Native 15-minute spread = DK2 day-ahead price minus DK1 day-ahead price, EUR/MWh.
- Material divergence event = absolute spread strictly greater than EUR 10/MWh. The threshold is fixed, not estimated from test prices.
- Source: cached and SHA-256-verified Energinet DayAheadPrices, 1 October 2025 inclusive through 1 October 2026 exclusive in Danish local time; same cache as Nordcast.
- Issue time: 10:00 Europe/Copenhagen on D−1 for every local delivery day. UTC keys distinguish repeated local times; days can contain 92/96/100 quarters.
- Every price becomes usable only 24 hours after its interval ends, a conservative research assumption. Archived revisions remain a limitation; there are no historical publication vintages.
- Features: DK1, DK2 and spread lags at 72/96/168/336 elapsed hours; mean/std/min/max/mean-absolute-spread/event-frequency over 96 quarters ending at the 72-hour lag; known local day/year harmonics, weekday indicators, UTC offset and DST fold. No future network, weather or generation data.

## Splits and recipes

Monthly updates for 1 June, 1 July, 1 August and 1 September 2026. Fit on 120 complete local days, followed by 28 separate calibration days ending at midnight two days before the first delivery day. Check that all calibration labels are available by the preceding day's issue time.

Regression recipes: constant zero spread; weekly spread lag; standardized ridge (alpha 10); histogram gradient boosting median (100 iterations, learning rate .05, 15 leaves, min samples/leaf 80, L2 1, no early stopping, seed 42). All four get symmetric marginal 80% intervals from the finite-sample 80th percentile of absolute errors on the separate calibration set.

Event-probability recipes: recent calibration-set frequency (Laplace smoothed); standardized logistic regression (C=1, max_iter=1000); histogram gradient boosting classifier (same tree settings). Logistic/tree probabilities are calibrated by isotonic regression on the 28-day calibration block; clipping handles scores outside its range. The recent-frequency baseline uses only calibration labels and has no features. Do not report these probabilities as calibrated merely because a calibration algorithm was applied.

Validation deliveries: 1–27 June. Choose regression by MAE and event probability by Brier score. Lock both model-family selections before the July issue. Test/replay deliveries: 1 July–30 September (92 days). Refit the fixed recipes monthly; later refits may use earlier test labels after maturation. No test-period model selection or parameter tuning.

Report regression MAE/RMSE/bias/coverage/width and skill against zero spread. Report probability Brier/log loss/ROC AUC/average precision, base rate and ten-bin reliability counts. Undefined metrics return null. A 0.60 probability threshold defines research alerts; it is fixed before evaluation. Report precision, recall and false alerts without changing the threshold to improve test results.

Compute a paired 95% descriptive bootstrap interval for each regression's MAE difference versus zero, resampling 92 daily error-difference blocks 2,000 times, seed 42. This preserves within-day dependence but not longer dependence and is not a formal model-selection significance test.

## Paper exposure

For q MW of consumption in DK2 versus a DK1 reference, quarter cost difference = q × 0.25 × spread. Positive means DK2 costs more. Sum signed differences for net daily cost; separately sum absolute quarter differences to show offsetting risk. Default q=1 MW; dashboard range 0–10 MW. Forecast exposure uses the June-selected regression, alerts the separately selected probability model. No order execution, profit, capacity ownership or tradable spread instrument is assumed. Network limits and physical feasibility are not estimated from price differences alone.

Summing marginal interval endpoints is an illustrative envelope, **not an 80% daily portfolio confidence interval**. Do not promote the alert threshold or exposure scale as an investment recommendation.
