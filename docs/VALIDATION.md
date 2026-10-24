# Verification record

24 October 2026. Local benchmark run completed using the predeclared protocol and the SHA-256-verified official cache. All four monthly folds completed. Selections: zero spread and recent frequency.

Local tests: 25 Python research/data/server tests and 5 Node browser-math/export tests. Tests cover DST days, feature and label cutoffs, duplicate/missing/nonfinite data, future-price mutation, strict event boundaries, interval ordering, probability endpoints/undefined metrics, constant-class calibration, deterministic bootstrap, exposure units/cancellation, source-to-spread reconciliation, all frozen metrics, protocol hash, full CSV rows, journal totals, and server path restrictions. Node checks reconcile exposure and reliability across languages and verify inspected-model CSV exports.

Browser interaction check: selected 30 September, boosted spread and logistic probability; set consumption to 10 MW. The exposure panel retained the June-selected zero model, as designed. Actual daily difference was €1,242.00, absolute differences €1,393.55, energy 240 MWh. Downloaded CSV contained 96 quarters, 10 MW throughout and the same actual cost sum. No source cache is needed to run the preview or tests.

Published code/data release: `5c68627772808335bce2d7f56f5fa95cdd77f1b9`. All 30 uploaded file hashes matched the staged Git manifest. Local checkout was synchronized to that commit with a clean working tree.

[GitHub Tests run 40136432778](https://github.com/Ehsan-Ch/danish-spread-risk-lab/actions/runs/40136432778): **success**. Python 3.11, Python 3.12 and Node 22 browser-math jobs all passed, including installation from the published package configuration. [Pages deployment run 40136432728](https://github.com/Ehsan-Ch/danish-spread-risk-lab/actions/runs/40136432728): **success**.

The [public preview](https://ehsan-ch.github.io/danish-spread-risk-lab/) loaded the full report. On the hosted page, changing to 30 September, inspecting the boosted model and choosing 10 MW reproduced the local selected-model exposure figures. Mobile viewport check at 390×844 (375-pixel content width with scrollbar) showed no horizontal document overflow. The two-area diagram, controls and content reflowed; tables scroll within their containers. Desktop layout and daily CSV download were also inspected locally. Full-page capture was unavailable in this browser, so the repository preview image is a normal viewport capture of the replay.

This verification-only documentation update leaves the tested code and data unchanged.
