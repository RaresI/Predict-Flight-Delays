"""Download and validate the OurAirports airport reference file."""

import logging
import sys
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import AIRPORTS_DIR, ORIGIN_AIRPORTS, ensure_directories

URL = "https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airports.csv"
OUTPUT = AIRPORTS_DIR / "airports.csv"
SELECTED_OUTPUT = AIRPORTS_DIR / "selected_airports.csv"

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

def main() -> None:
    ensure_directories()
    logging.info("Downloading OurAirports data from %s", URL)
    response = requests.get(URL, timeout=60)
    response.raise_for_status()
    OUTPUT.write_bytes(response.content)
    airports = pd.read_csv(OUTPUT, low_memory=False)
    selected = airports[airports["iata_code"].isin(ORIGIN_AIRPORTS)].copy()
    required = {"iata_code", "latitude_deg", "longitude_deg", "elevation_ft", "iso_country"}
    missing = required - set(selected.columns)
    if missing:
        raise ValueError(f"OurAirports file is missing required columns: {sorted(missing)}")
    selected = selected.drop_duplicates("iata_code")
    absent = set(ORIGIN_AIRPORTS) - set(selected["iata_code"])
    if absent:
        raise ValueError(f"Selected airports absent from OurAirports: {sorted(absent)}")
    selected.to_csv(SELECTED_OUTPUT, index=False)
    logging.info("Saved %d selected airports to %s", len(selected), SELECTED_OUTPUT)

if __name__ == "__main__":
    main()
