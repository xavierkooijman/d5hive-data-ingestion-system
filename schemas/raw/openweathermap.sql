CREATE TABLE IF NOT EXISTS openweathermap (
    hostfeed VARCHAR(50),
    source VARCHAR(50),
    tstamp TIMESTAMPZ,
    latitude DOUBLE,
    longitude DOUBLE,
    temperature_celsius REAL,
    wind_speed_kmh REAL,
    wind_direction_degrees INTEGER,
    wind_gust_kmh REAL,
    sea_level_pressure_hpa REAL,
    ground_level_pressure_hpa REAL,
    humidity_percentage REAL,
    cloudiness_percentage REAL,
    visibility_meters INTEGER,
    precipitation_mm REAL,
    PRIMARY KEY (tstamp, latitude, longitude)
)