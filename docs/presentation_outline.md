# Phase 1 presentation outline

1. **Problem and objective** — research question, target definition and why departure delay matters.
2. **Three data sources** — BTS, OurAirports and Open-Meteo, with a source-to-feature mapping.
3. **Integration pipeline** — BTS local time → IANA timezone → UTC hour → weather join.
4. **Dataset design** — one row per flight, input features, target and leakage exclusions.
5. **Actual results** — show `validation_report.json`, a five-row sample and one table of missingness/delay rate.
6. **Phase 2 plan** — EDA, chronological split, Logistic Regression, Random Forest and XGBoost.
7. **Limitations and next steps** — reanalysis limitation, destination weather and model benchmarking.

Use the generated sample CSV and actual validation report rather than invented screenshots or statistics.
