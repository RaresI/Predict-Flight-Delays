"""Shared configuration for the flight-delay dataset pipeline."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
BTS_DIR = RAW_DIR / "bts"
AIRPORTS_DIR = RAW_DIR / "airports"
WEATHER_DIR = RAW_DIR / "weather"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SAMPLES_DIR = PROJECT_ROOT / "data" / "samples"

START_DATE = "2025-01-01"
END_DATE = "2025-12-31"
ORIGIN_AIRPORTS = ("ATL", "ORD", "DFW", "DEN", "JFK")
WEATHER_VARIABLES = (
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "rain",
    "snowfall",
    "weather_code",
    "pressure_msl",
    "cloud_cover",
    "wind_speed_10m",
    "wind_gusts_10m",
    "wind_direction_10m",
)

BTS_COLUMNS = [
    "FlightDate", "Year", "Quarter", "Month", "DayofMonth", "DayOfWeek",
    "Reporting_Airline", "Flight_Number_Reporting_Airline", "Origin", "Dest",
    "OriginAirportID", "DestAirportID", "CRSDepTime", "DepTime", "DepDelay",
    "DepDelayMinutes", "DepDel15", "CRSArrTime", "ArrTime", "ArrDelay",
    "ArrDel15", "Cancelled", "CancellationCode", "Diverted", "Distance",
    "CRSElapsedTime", "ActualElapsedTime", "TaxiOut", "TaxiIn",
    "CarrierDelay", "WeatherDelay", "NASDelay", "SecurityDelay",
    "LateAircraftDelay",
]

def ensure_directories() -> None:
    for path in (BTS_DIR, AIRPORTS_DIR, WEATHER_DIR, PROCESSED_DIR, SAMPLES_DIR):
        path.mkdir(parents=True, exist_ok=True)
