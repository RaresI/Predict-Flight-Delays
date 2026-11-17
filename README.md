# Predicting Flight Delays Using Flight and Weather Information

This project builds an original flight-level dataset by integrating official BTS flight records, OurAirports airport coordinates and Open-Meteo historical hourly weather.

## Research question

Can historical weather conditions and flight characteristics predict whether a scheduled flight departs at least 15 minutes late?

The target is `dep_delayed_15`, derived from BTS `DepDel15`: `0` means less than 15 minutes late and `1` means at least 15 minutes late.

## Scope

- Dates: January 1, 2025 through December 31, 2025
- Origin airports: ATL, ORD, DFW, DEN and JFK
- Unit of analysis: one row per valid, non-cancelled flight
- Weather: hourly Open-Meteo reanalysis at the origin airport

## Reproducible pipeline

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/download_airports.py
python src/download_bts.py
python src/fetch_weather.py
python src/build_dataset.py
python src/validate_dataset.py
```

The BTS interface may require manual downloads. If the official bulk endpoint is unavailable, place the monthly BTS ZIP files in `data/raw/bts/` and rerun the pipeline.

## Outputs

- `data/processed/flight_weather_dataset.csv`
- `data/samples/flight_weather_sample.csv`
- `data/processed/build_statistics.json`
- `data/processed/validation_report.json`

Raw data is intentionally excluded from Git because the files are large. See `docs/data_sources.md` for provenance and limitations.
