# Beltline · Danish Spread Risk Lab

[Live interactive replay](https://ehsan-ch.github.io/danish-spread-risk-lab/) · [Research protocol](docs/PROTOCOL.md) · [Model card](docs/MODEL_CARD.md)

How much will Danish electricity price areas diverge, and what does that difference mean for a constant load? Beltline forecasts **DK2 minus DK1** at 15-minute resolution, compares event probabilities for **absolute spread > €10/MWh**, and turns the spread into a transparent paper basis-exposure calculation.

The main result is deliberately unglamorous: **the simple baselines won**. The project demonstrates chronological evaluation, calibrated-model diagnostics, reproducible evidence and honest model rejection, rather than a claim of profitable trading.

![Beltline interactive research preview](reports/preview.jpg)

## Results

Families selected using 1–27 June 2026 only. Replay: 1 July–30 September, 92 days / 8,832 quarters. Recipes refit monthly using matured historical labels. Source/calendar had already been examined in Nordcast; this is not a pristine independent holdout.

| Spread model | Test MAE €/MWh | Nominal 80% interval coverage |
|---|---:|---:|
| **Zero spread — selected** | **3.316** | 78.9% |
| Weekly lag | 5.377 | 80.9% |
| Standardized ridge | 11.676 | 57.5% |
| Boosted median | 3.798 | 81.1% |

| Event model | Test Brier score (lower is better) | ROC AUC |
|---|---:|---:|
| **Recent frequency — selected** | **0.07170** | 0.489 |
| Logistic + isotonic | 0.07714 | 0.468 |
| Boosted + isotonic | 0.07307 | 0.475 |

There were **673 divergence quarters (7.62%)**. All three probability models generated **zero alerts at the predeclared 60% threshold**, so recall was 0% and precision was undefined. These are poor alerting models on this replay; calibration machinery is not proof of calibration. The zero model's low average error hides tail risk. The boosted model's daily paired MAE difference versus zero was +0.48 €/MWh, descriptive 95% daily bootstrap interval approximately [+0.33, +0.64]. See full precision and all models in `reports/benchmark/results.json`.

## Use the project

The [public preview](https://ehsan-ch.github.io/danish-spread-risk-lab/) needs no account, server or API key. Choose a delivery day, compare forecast families and probabilities, vary paper consumption from 0 to 10 MW, and download quarter-level evidence. The exposure panel always uses the June-selected spread model; the daily download uses the models currently being inspected and labels the columns explicitly.

For local development (Python 3.11 or 3.12):

```sh
python -m venv .venv
# Activate .venv using your shell's usual command.
python -m pip install -e .
python -m beltline.cli serve
# Open http://127.0.0.1:8790/
python -m unittest discover -s tests -v
node --test tests/core.test.mjs
```

Rebuild the benchmark from official data:

```sh
python -m beltline.cli download --cache data
python -m beltline.cli run --cache data --output reports/custom
```

The downloader requires a fresh cache to avoid silently replacing provenance. To refresh an existing cache use a new directory. Rebuilt outputs go into `reports/custom` by default; the preview intentionally loads the frozen `reports/benchmark`. Compare artifacts before intentionally replacing that benchmark. Full training takes a few minutes on a CPU; no paid service or GPU is required. Dependencies are pinned. Archived API data may be revised, so a later download is not guaranteed to recreate the original cache hash or exact model outputs. The published full-precision predictions are a self-contained audit artifact, not enough to reconstruct all training features without the source cache.

## Research design

- Official Energinet native-quarter prices: 1 October 2025 inclusive to 1 October 2026 exclusive, Danish local boundaries, 70,080 rows. Negative prices retained; gaps, duplicates and nonfinite values rejected.
- A day-ahead issue at 10:00 Copenhagen on D−1. Every price has an assumed availability delay of 24 hours after its interval ends. Features use 72/96/168/336-hour elapsed lags, lagged spread statistics and known calendar information.
- 120 fitting days and 28 separate calibration days. Monthly model updates in June, July, August and September. Calibration labels mature before each first issue; later monthly fits may use earlier replay labels.
- Separate regression and probability selections in June. Finite-sample absolute-residual intervals and isotonic probability calibration use calibration data only. All recipes, target thresholds and selection rules are in the fixed protocol.
- A 2,000-draw paired bootstrap samples daily MAE-difference blocks. This preserves within-day dependence but ignores longer dependence; it is descriptive, not a formal selection significance test.

## Paper exposure, not arbitrage

For q MW of DK2 consumption compared with a DK1 reference:

`quarter cost difference = q × 0.25 hours × (DK2 − DK1) EUR/MWh`

The journal includes net signed cost, absolute differences, point forecast cost and an illustrative envelope from summed marginal endpoints. The envelope is **not an 80% daily portfolio interval**. Negative differences mean DK2 was cheaper. No orders, hedges, capacity rights, physical delivery, transaction costs or profit are modeled. Price differences alone cannot identify a specific interconnector bottleneck.

## Layout

`beltline/` contains the data checks, feature cutoffs, models, evaluation, exposure math and local server. `web/` and `index.html` provide a static preview with no external scripts or fonts. `reports/benchmark/` stores results, all 11,424 validation-plus-test quarter forecasts in compressed CSV, and the 92-day selected-model exposure journal. `tests/` checks the research contracts and reconciles browser math with Python outputs. CI tests Python 3.11/3.12 and Node 22 without downloading fresh market data.

## License and limitations

Original code/documentation: MIT. Energinet data and adapted data-derived reports: CC BY 4.0 with attribution; see [ATTRIBUTION.md](ATTRIBUTION.md). Data adapter and source cache methodology reuse the author's [Nordcast](https://github.com/Ehsan-Ch/danish-power-forecast-lab) project. This is a portfolio research study, not a production forecast service, an independent prospective trial or an investment recommendation. No model weights or live updates are served. See the [model card](docs/MODEL_CARD.md) and [verification record](docs/VALIDATION.md).
