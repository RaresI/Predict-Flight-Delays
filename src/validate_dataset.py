"""Validate the processed dataset and write actual Phase 1 statistics."""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import PROCESSED_DIR, ORIGIN_AIRPORTS

REQUIRED_FEATURES = {
    "flight_date", "day_of_week", "month", "carrier", "flight_number",
    "origin", "destination", "scheduled_departure_time", "scheduled_departure_hour",
    "distance", "origin_latitude", "origin_longitude", "temperature_2m",
    "relative_humidity_2m", "precipitation", "rain", "snowfall", "weather_code",
    "pressure_msl", "cloud_cover", "wind_speed_10m", "wind_gusts_10m",
    "wind_direction_10m",
}

def main() -> None:
    path = PROCESSED_DIR / "flight_weather_dataset.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run build_dataset.py first.")
    df = pd.read_csv(path)
    feature_columns = [c for c in df.columns if c not in {"flight_id", "dep_delayed_15"}]
    errors = []
    if len(df) < 1000:
        errors.append(f"fewer than 1,000 records: {len(df)}")
    if len(feature_columns) < 10:
        errors.append(f"fewer than 10 input features: {len(feature_columns)}")
    if not set(df["dep_delayed_15"].dropna().unique()).issubset({0, 1}):
        errors.append("target contains values other than 0 and 1")
    if df["flight_id"].duplicated().any():
        errors.append("duplicate flight identifiers found")
    if not set(df["origin"]).issubset(ORIGIN_AIRPORTS):
        errors.append("unexpected origin airport found")
    weather_columns = [c for c in REQUIRED_FEATURES if c in df.columns and c not in {"flight_date"}]
    statistics = {
        "final_records": int(len(df)),
        "input_feature_count": len(feature_columns),
        "date_min": str(df["flight_date"].min()),
        "date_max": str(df["flight_date"].max()),
        "origin_count": int(df["origin"].nunique()),
        "origins": sorted(df["origin"].dropna().unique().tolist()),
        "carrier_count": int(df["carrier"].nunique()),
        "delay_rate_percent": round(float(df["dep_delayed_15"].mean() * 100), 2),
        "duplicate_flight_ids": int(df["flight_id"].duplicated().sum()),
        "weather_match_percent": round(float(df["temperature_2m"].notna().mean() * 100), 2),
        "missing_percent": (df[weather_columns].isna().mean() * 100).round(2).to_dict(),
        "weather_range_checks": {
            "relative_humidity_outside_0_100": int(((df["relative_humidity_2m"] < 0) | (df["relative_humidity_2m"] > 100)).sum()),
            "wind_speed_negative": int((df["wind_speed_10m"] < 0).sum()),
            "precipitation_negative": int((df["precipitation"] < 0).sum()),
        },
        "validation_errors": errors,
        "validation_passed": not errors,
    }
    output = PROCESSED_DIR / "validation_report.json"
    output.write_text(json.dumps(statistics, indent=2), encoding="utf-8")
    print(json.dumps(statistics, indent=2))
    if errors:
        raise SystemExit("Validation failed: " + "; ".join(errors))

if __name__ == "__main__":
    main()
