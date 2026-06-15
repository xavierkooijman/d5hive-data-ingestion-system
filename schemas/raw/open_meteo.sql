CREATE TABLE IF NOT EXISTS open_meteo (
    hostfeed VARCHAR(50),
    source VARCHAR(50),
    tstamp TIMESTAMPTZ,
    latitude DOUBLE,
    longitude DOUBLE,
    temperature_celsius REAL,
    wind_speed_kmh REAL,
    wind_direction_degrees INTEGER,
    PRIMARY KEY (tstamp, latitude, longitude)
)