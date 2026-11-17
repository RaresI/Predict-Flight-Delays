# Phase 1 report

## 1. Objective

This project investigates whether historical weather conditions and scheduled flight characteristics can predict whether a US domestic flight departs at least 15 minutes late. It is a supervised binary classification problem.

## 2. Dataset construction

The dataset is constructed rather than taken from a prepared flight-weather dataset. BTS supplies the flight-level observations and the official departure-delay label. OurAirports supplies airport coordinates. Open-Meteo supplies hourly historical weather for each origin airport. Local scheduled departure times are converted through IANA time zones before matching to UTC weather hours.

## 3. Scope and quality controls

The intended scope is the full 2025 calendar year and five major airports: ATL, ORD, DFW, DEN and JFK. Cancelled flights and records without a valid target or scheduled departure timestamp are excluded. The validation script checks row counts, feature count, binary labels, duplicate flight identifiers, weather coverage, data types, ranges and row-count preservation after joins.

The completed run produced 1,356,303 valid flight rows, 27 input features, five origin airports and 14 reporting carriers. The observed delayed-flight rate is 25.32%. There are no duplicate flight identifiers, 99.95% of rows have a matched weather record, and all validation checks passed. The full machine-readable results are in `data/processed/validation_report.json`.

## 4. Intended analysis

Phase 2 will examine delay rates by airport, airline, month, weekday and scheduled departure hour. It will also analyze associations between weather variables and delays, investigate correlations and produce feature-importance results.

## 5. Planned algorithms

Logistic Regression will be used as an interpretable baseline. Random Forest will model nonlinear relationships and interactions with limited preprocessing. XGBoost will provide a strong gradient-boosted tree benchmark for structured data. Accuracy, precision, recall, F1-score, ROC-AUC, PR-AUC and confusion matrices will be reported, with special attention to class imbalance. A chronological split will better simulate predictions on future flights.

## 6. Limitations

Open-Meteo historical weather is reanalysis and is not equivalent to a forecast available before departure. Airport-coordinate weather may not represent every runway or terminal. Operational causes of delay are only partially observed. The initial dataset uses origin weather only; destination weather is a possible extension.
