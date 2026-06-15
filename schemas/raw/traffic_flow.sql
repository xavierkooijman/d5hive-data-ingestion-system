CREATE TABLE IF NOT EXISTS tomtom_traffic_flow (
    source VARCHAR(50),
    frc VARCHAR(10),
    tstamp TIMESTAMPTZ,
    current_speed_kmh REAL,
    free_flow_speed_kmh REAL,
    current_travel_time_s REAL,
    free_flow_travel_time_s REAL,
    confidence REAL,
    road_closure BOOLEAN,
    flow_segment_geometry JSON,
);