CREATE TABLE IF NOT EXISTS postos_abastecimento (
    globalId UUID PRIMARY KEY,
    source VARCHAR(50),
    brand VARCHAR(50),
    latitude DOUBLE,
    longitude DOUBLE,
    tstamp TIMESTAMPTZ
);