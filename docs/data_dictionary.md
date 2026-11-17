# Data dictionary

| Column | Meaning | Type | Source | Role |
|---|---|---|---|---|
| flight_id | Deterministic flight-level identifier | string | Derived | Audit key |
| flight_date | Scheduled flight date | date | BTS | Input |
| day_of_week | Day of week | integer | BTS | Input |
| month | Month number | integer | BTS | Input |
| carrier | Reporting airline code | string | BTS | Input |
| flight_number | Reporting flight number | integer | BTS | Input |
| origin | Origin airport IATA code | string | BTS | Input |
| destination | Destination airport IATA code | string | BTS | Input |
| scheduled_departure_time | Local scheduled departure HHMM | integer | BTS | Input |
| scheduled_departure_utc | Converted UTC timestamp | datetime | Derived | Input |
| scheduled_departure_hour | Local scheduled departure hour | integer | Derived | Input |
| distance | Scheduled flight distance in miles | numeric | BTS | Input |
| scheduled_elapsed_time | Scheduled elapsed time in minutes | numeric | BTS | Input |
| origin_latitude / origin_longitude | Airport coordinates | numeric | OurAirports | Input |
| origin_elevation_ft | Airport elevation | numeric | OurAirports | Input |
| origin_timezone | IANA origin time zone | string | Derived | Input |
| temperature_2m | Air temperature at 2 m, °C | numeric | Open-Meteo | Input |
| relative_humidity_2m | Relative humidity at 2 m, % | numeric | Open-Meteo | Input |
| precipitation / rain / snowfall | Hourly precipitation amounts, mm | numeric | Open-Meteo | Input |
| weather_code | WMO weather interpretation code | integer | Open-Meteo | Input |
| pressure_msl | Mean sea-level pressure, hPa | numeric | Open-Meteo | Input |
| cloud_cover | Total cloud cover, % | numeric | Open-Meteo | Input |
| wind_speed_10m / wind_gusts_10m | Wind speed and gusts at 10 m, km/h | numeric | Open-Meteo | Input |
| wind_direction_10m | Wind direction at 10 m, degrees | numeric | Open-Meteo | Input |
| dep_delayed_15 | Departure delay of at least 15 minutes | binary | BTS `DepDel15` | Target |

Post-departure variables such as actual departure time, actual delay minutes, arrival delay and delay causes are deliberately excluded from the modeling dataset to avoid leakage.
