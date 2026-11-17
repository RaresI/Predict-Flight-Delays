"""Download monthly BTS On-Time Reporting Carrier files for 2025.

The PREZIP endpoint is the official BTS bulk-download location used by the
TranStats download interface. If BTS changes the endpoint, the script fails
with the exact URL so the file can be downloaded manually and placed in
data/raw/bts/.
"""

import logging
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import BTS_DIR, ensure_directories

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

def main() -> None:
    ensure_directories()
    for month in range(1, 13):
        name = f"On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2025_{month}.zip"
        path = BTS_DIR / name
        url = f"https://transtats.bts.gov/PREZIP/{name}"
        if path.exists() and path.stat().st_size > 0:
            logging.info("Already present: %s", path)
            continue
        logging.info("Downloading %s", url)
        response = requests.get(url, timeout=180)
        if response.status_code != 200 or not response.content.startswith(b"PK"):
            raise RuntimeError(
                f"BTS download failed for month {month}: HTTP {response.status_code}. "
                f"Download the official file manually from {url} into {path}."
            )
        path.write_bytes(response.content)
        logging.info("Saved %.1f MB", len(response.content) / 1024**2)

if __name__ == "__main__":
    main()
