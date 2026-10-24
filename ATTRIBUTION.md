# Attribution and sources

**Energinet / Energy Data Service — DayAheadPrices**, retrieved 24 October 2026. Dataset: https://www.energidataservice.dk/tso-electricity/DayAheadPrices . Metadata: https://api.energidataservice.dk/meta/dataset/DayAheadPrices . Terms: https://www.energidataservice.dk/terms-and-conditions . License: [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/).

Changes: selected DK1/DK2 records for the fixed study window, calculated differences and lag features, fitted forecasting models, and produced derived charts, metrics and exposure calculations. No endorsement by Energinet is implied. Source data and data-derived reports retain CC BY 4.0 attribution; the repository's MIT license covers original code and documentation.

Raw source SHA-256: `93ccd57867b2eae79705659e84a4aa8f1913b3a714204ccb859316a964ef7da2`.

Metadata SHA-256: `f96149b61c23e1c85ce2023b9859fb250d178cf83445f6e488bdde2a0410a162`.

The complete retrieval URL and UTC timestamp are recorded in the report's source manifest. The source adapter and conservative availability convention reuse Ehsan Cheraghi's MIT-licensed [Nordcast](https://github.com/Ehsan-Ch/danish-power-forecast-lab).

Market context: [Nord Pool price calculation](https://www.nordpoolgroup.com/en/trading/Day-ahead-trading/Price-calculation/) and [capacity allocation](https://www.nordpoolgroup.com/en/trading/Day-ahead-trading/capacities/). Bidding areas can diverge under network constraints; day-ahead capacity is allocated implicitly. A measured DK2−DK1 spread is not itself an executable arbitrage or proof of congestion on a particular cable.
