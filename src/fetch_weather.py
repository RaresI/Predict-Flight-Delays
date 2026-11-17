"""Fetch cached hourly Open-Meteo reanalysis weather for selected airports."""

import json
import logging
import sys
import time
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import AIRPORTS_DIR, END_DATE, START_DATE, WEATHER_DIR, WEATHER_VARIABLES, ensure_directories

# Kept as a constant to make the source and query auditable.
API_URL = "https://archive-api.open-meteo.com/v1/archive"
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

def main() -> None:
    ensure_directories()
    airports = pd.read_csv(AIRPORTS_DIR / "selected_airports.csv")
    for row in airports.to_dict("records"):
        code = row["iata_code"]
        output = WEATHER_DIR / f"{code}_2025.json"
        if output.exists():
            logging.info("Already present: %s", output)
            continue
        params = {
            "latitude": row["latitude_deg"],
            "longitude": row["longitude_deg"],
            "start_date": START_DATE,
            "end_date": END_DATE,
            "hourly": ",".join(WEATHER_VARIABLES),
            "timezone": "UTC",
        }
        for attempt in range(3):
            try:
                response = requests.get(API_URL, params=params, timeout=180)
                response.raise_for_status()
                payload = response.json()
                if "hourly" not in payload:
                    raise ValueError(f"Open-Meteo response has no hourly data: {payload}")
                output.write_text(json.dumps(payload), encoding="utf-8")
                logging.info("Saved weather for %s", code)
                break
            except (requests.RequestException, ValueError) as exc:
                if attempt == 2:
                    raise RuntimeError(f"Weather request failed for {code}") from exc
                time.sleep(2**attempt)

if __name__ == "__main__":
    main()
