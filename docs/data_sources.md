# Data sources and provenance

## Bureau of Transportation Statistics

Source: [TranStats On-Time Performance](https://transtats.bts.gov/ONTIME/). The BTS Reporting Carrier On-Time Performance table supplies flight-level schedules, airports, carrier identifiers, distance and the `DepDel15` departure-delay label. Cancelled flights are excluded because they did not depart.

## OurAirports

Source: [OurAirports open data](https://ourairports.com/data/), distributed through the [ourairports-data repository](https://github.com/davidmegginson/ourairports-data). `airports.csv` supplies IATA codes and airport coordinates. Coordinates are used to resolve IANA time zones and request weather.

## Open-Meteo

Source: [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api). Hourly variables are requested from the archive endpoint with `timezone=UTC`. The weather is historical reanalysis, not the forecast that would have been available operationally before departure.

## Joining rule

BTS scheduled departure time is expressed in origin-airport local time. It is converted to an aware timestamp using the airport's IANA time zone, then converted to UTC and floored to the hour. The weather join uses `origin` and this UTC hour. The implementation uses pandas merge validation to prevent one-to-many row multiplication.
