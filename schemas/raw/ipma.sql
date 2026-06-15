CREATE TABLE IF NOT EXISTS ipma (
    hostfeed VARCHAR(50),
    source VARCHAR(50),
    tstamp TIMESTAMPZ,
    latitude DOUBLE,
    longitude DOUBLE,
    temperature_celsius REAL,
    wind_speed_kmh REAL,
    wind_direction_degrees INTEGER,
    humidity_percentage REAL,
    pressure_hpa REAL,
    precipitation_mm REAL,
    radiation_kjm2 REAL,
    PRIMARY KEY (tstamp, latitude, longitude)
)