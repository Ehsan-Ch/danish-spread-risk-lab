# Model card

## Purpose

Beltline evaluates Danish DK2−DK1 quarter-hour day-ahead spread forecasts and probabilities of absolute spread exceeding €10/MWh. Intended use: reproducible research and demonstrating energy-analysis engineering. Intended users: analysts and reviewers. Not suitable for automatic execution, credit decisions, physical dispatch or unreviewed operational alerts.

## Inputs and targets

33 features: twelve DK1/DK2/spread lags (72, 96, 168, 336 elapsed hours); six statistics from 96 quarters ending at the 72-hour lag; six periodic calendar features; seven weekdays; UTC offset; DST fold. Prices are in EUR/MWh, UTC keys are unique, and Danish delivery days respect 23/24/25-hour changes. Targets are signed spread and the strictly greater-than-10 absolute-spread event.

All source prices are assumed usable only after interval end +24 hours. Feature readiness is checked against D−1 10:00 local. The benchmark has at least nine hours of feature-availability margin. This does not establish actual point-in-time publication availability: historical revisions and missing publication vintages remain limitations.

## Fitting and selection

See [the fixed protocol](PROTOCOL.md) for exact hyperparameters. All candidate families train on the same 120-day blocks; 28 following days are held out for residual and isotonic calibration. The frequency baseline is Laplace-smoothed calibration prevalence. Selection uses June validation MAE and Brier respectively. Selected families remain fixed during the July–September monthly replay, but parameters/calibrators update with matured history. There is no random train/test split or tuning on replay outcomes.

The source period/calendar had been used in an earlier project. This protocol was written before Beltline's comparison, but familiar benchmark reuse means results should not be described as independent prospective evidence.

## Observed performance and failure modes

Zero spread won validation and later MAE (3.3155 €/MWh). The selected 80% interval covered 78.87% of replay quarters. Recent frequency won Brier (0.07170). Its pooled ROC AUC was 0.489; it is constant within each monthly fold but differs between folds. It has no within-fold discrimination. Learned alternatives did not improve Brier or MAE. Ridge was especially unstable across regimes.

No model probability reached the fixed 0.60 alert threshold. All 673 event quarters were missed by that alert rule. Low average error mostly reflects small/converged spreads and does not validate an ability to anticipate extremes. The plots and full CSV retain negative spreads and large misses; no favorable subset replaces the full-period comparison. Isotonic calibration can be noisy, especially with rare events and a small, temporally shifted calibration set. No conditional calibration or coverage guarantee is claimed.

## What is missing

No weather, load, renewable forecasts, fuel prices, neighboring prices, network topology, outages or cross-border capacity inputs. No publication vintages, external market validation, prospective monitoring, execution simulator, transaction-cost accounting or capacity-rights model. A future extension should freeze new prospective dates and obtain timestamped exogenous forecasts before fitting new recipes. It should not retune against this reported replay and call the same dates a new holdout.

## Uncertainty and exposure

Absolute-residual intervals are symmetric around each point forecast and nominally marginal 80%; temporal dependence and regime drift limit coverage. Summed endpoints are not a joint portfolio distribution. The descriptive daily bootstrap uses 92 blocks and ignores dependence beyond a day. Exposure is a dimensional calculation for constant load, not a tradable instrument or a risk limit recommendation.

## Reproducibility and data handling

Source/cache hashes, protocol hash, package versions, monthly fit/calibration boundaries, selected families and all metrics are embedded in `reports/benchmark/results.json`. Raw source cache is excluded from Git; API retrieval can change with archive revisions. The downloadable predictions preserve full floating-point precision. No personal data, credentials or tracking analytics are collected by the preview. Rendering is entirely local to the viewer's browser after static asset retrieval.
