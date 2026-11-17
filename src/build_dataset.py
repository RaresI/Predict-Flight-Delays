"""Build one flight-level dataset by joining BTS, OurAirports and Open-Meteo."""

import json
import logging
import sys
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from timezonefinder import TimezoneFinder

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import BTS_COLUMNS, BTS_DIR, AIRPORTS_DIR, END_DATE, ORIGIN_AIRPORTS, PROCESSED_DIR, SAMPLES_DIR, WEATHER_DIR, ensure_directories

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
TF = TimezoneFinder()

def parse_local_departure(date_value: object, time_value: object, timezone: str) -> tuple[pd.Timestamp, int] | tuple[None, None]:
    if pd.isna(date_value) or pd.isna(time_value):
        return None, None
    try:
        date = pd.Timestamp(date_value).date()
        numeric = int(float(time_value))
        if numeric == 2400:
            local = datetime.combine(date + timedelta(days=1), datetime.min.time())
        else:
            hour, minute = divmod(numeric, 100)
            if hour > 23 or minute > 59:
                return None, None
            local = datetime.combine(date, datetime.min.time()).replace(hour=hour, minute=minute)
        aware = local.replace(tzinfo=ZoneInfo(timezone))
        utc = pd.Timestamp(aware).tz_convert("UTC")
        return utc, hour if numeric != 2400 else 0
    except (TypeError, ValueError, ZoneInfo):
        return None, None

def load_bts() -> pd.DataFrame:
    frames = []
    for path in sorted(BTS_DIR.glob("*.zip")):
        with zipfile.ZipFile(path) as archive:
            csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if len(csv_names) != 1:
                raise ValueError(f"Expected one CSV in {path.name}, found {csv_names}")
            with archive.open(csv_names[0]) as csv_file:
                frame = pd.read_csv(csv_file, usecols=lambda c: c in BTS_COLUMNS, low_memory=False)
        frames.append(frame)
    if not frames:
        raise FileNotFoundError("No BTS ZIP files found in data/raw/bts/. Run download_bts.py first.")
    flights = pd.concat(frames, ignore_index=True)
    flights = flights[flights["Origin"].isin(ORIGIN_AIRPORTS)].copy()
    flights = flights[flights["Cancelled"].fillna(0).eq(0)]
    flights = flights[flights["DepDel15"].isin([0, 1])].copy()
    return flights

def load_weather() -> pd.DataFrame:
    frames = []
    for path in sorted(WEATHER_DIR.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        hourly = pd.DataFrame(payload["hourly"])
        hourly["weather_time_utc"] = pd.to_datetime(hourly.pop("time"), utc=True)
        hourly["origin"] = path.stem.split("_")[0]
        frames.append(hourly)
    if not frames:
        raise FileNotFoundError("No weather JSON files found. Run fetch_weather.py first.")
    weather = pd.concat(frames, ignore_index=True)
    return weather.drop_duplicates(["origin", "weather_time_utc"])

def main() -> None:
    ensure_directories()
    airports = pd.read_csv(AIRPORTS_DIR / "selected_airports.csv")
    airports["origin_timezone"] = airports.apply(
        lambda r: TF.timezone_at(lng=float(r["longitude_deg"]), lat=float(r["latitude_deg"])), axis=1
    )
    if airports["origin_timezone"].isna().any():
        raise ValueError("Could not resolve a timezone for every selected airport.")
    flights = load_bts()
    flights["scheduled_departure_utc"], flights["scheduled_departure_hour"] = zip(*flights.apply(
        lambda r: parse_local_departure(r["FlightDate"], r["CRSDepTime"], airports.set_index("iata_code").loc[r["Origin"], "origin_timezone"]),
        axis=1
    ))
    invalid_timestamps = int(flights["scheduled_departure_utc"].isna().sum())
    flights = flights.dropna(subset=["scheduled_departure_utc"]).copy()
    flights["weather_time_utc"] = flights["scheduled_departure_utc"].dt.floor("h")
    flights["flight_id"] = (
        flights["FlightDate"].astype(str) + "|" + flights["Reporting_Airline"].astype(str) + "|" +
        flights["Flight_Number_Reporting_Airline"].astype(str) + "|" + flights["Origin"] + "|" +
        flights["Dest"] + "|" + flights["CRSDepTime"].astype(str)
    )
    if flights["flight_id"].duplicated().any():
        logging.warning("Duplicate flight identifiers found; retaining rows and reporting them in validation.")
    weather = load_weather()
    merged = flights.merge(airports[["iata_code", "latitude_deg", "longitude_deg", "elevation_ft", "origin_timezone"]],
                           left_on="Origin", right_on="iata_code", validate="many_to_one")
    merged = merged.merge(
        weather,
        left_on=["Origin", "weather_time_utc"],
        right_on=["origin", "weather_time_utc"],
        how="left",
        validate="many_to_one",
        suffixes=("", "_weather"),
    )
    merged = merged.drop(columns=["origin"])
    output_columns = [
        "flight_id", "flight_date", "day_of_week", "month", "carrier",
        "flight_number", "origin", "destination", "scheduled_departure_time",
        "scheduled_departure_utc", "scheduled_departure_hour", "distance",
        "scheduled_elapsed_time", "origin_latitude", "origin_longitude",
        "origin_elevation_ft", "origin_timezone", "dep_delayed_15", *[c for c in [
            "temperature_2m", "relative_humidity_2m", "precipitation", "rain",
            "snowfall", "weather_code", "pressure_msl", "cloud_cover",
            "wind_speed_10m", "wind_gusts_10m", "wind_direction_10m"
        ] if c in merged.columns]
    ]
    merged["dep_delayed_15"] = merged["DepDel15"].astype("int8")
    final = merged.rename(columns={
        "FlightDate": "flight_date", "DayOfWeek": "day_of_week", "Month": "month",
        "Reporting_Airline": "carrier", "Flight_Number_Reporting_Airline": "flight_number",
        "Origin": "origin", "Dest": "destination", "CRSDepTime": "scheduled_departure_time",
        "Distance": "distance", "CRSElapsedTime": "scheduled_elapsed_time",
        "latitude_deg": "origin_latitude", "longitude_deg": "origin_longitude",
        "elevation_ft": "origin_elevation_ft",
    })
    final = final[[c for c in output_columns if c in final.columns]]
    final.to_csv(PROCESSED_DIR / "flight_weather_dataset.csv", index=False)
    final.sample(min(100, len(final)), random_state=42).to_csv(SAMPLES_DIR / "flight_weather_sample.csv", index=False)
    stats = {
        "bts_filtered_records": int(len(flights) + invalid_timestamps),
        "invalid_timestamp_records": invalid_timestamps,
        "final_records": int(len(final)),
        "weather_matched_records": int(final["temperature_2m"].notna().sum()),
        "duplicate_flight_ids": int(final["flight_id"].duplicated().sum()),
    }
    (PROCESSED_DIR / "build_statistics.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    logging.info("Built %d final records", len(final))

if __name__ == "__main__":
    main()
