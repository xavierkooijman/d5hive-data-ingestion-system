from ingestion.sources.api import APIClient
from ingestion.transformations.common import wind_direction_to_degrees
from ingestion.transformations.time import normalize_string_timestamp
from utils.connectors import run_inserts
import logging


def run(config):
    logger = logging.getLogger(__name__)

    logger.info(f"Pipeline {config['pipeline_name']} Started")

    apiClient = APIClient(config["source"]["base_url"])
    raw_data = apiClient.get(config["source"]["endpoint"])

    logger.info(
        f"Filtering {len(raw_data.get('features', []))} rows of data for station ID {config['source']['station_id']}")

    features = []
    for feature in raw_data.get("features", []):
        if feature['properties'].get('idEstacao') == config["source"]["station_id"]:
            features.append(feature)

    logger.info(
        f"Filtered down to {len(features)} rows of data for station ID {config['source']['station_id']}")

    data = []

    logger.info("Normalizing and transforming data")

    for feature in features:
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get(
            "coordinates", [None, None])

        data.append({
            "hostfeed": "hostfeed",
            "source": config["source"]["name"],
            "tstamp": normalize_string_timestamp(props.get("time"), config["source"]["timezone"]),
            "latitude": coords[1],
            "longitude": coords[0],
            "temperature_celsius": props.get("temperatura"),
            "wind_speed_kmh": props.get("intensidadeVentoKM"),
            "wind_direction_degrees": wind_direction_to_degrees(props.get("descDirVento")),
            "humidity_percentage": None if props.get("humidade") == -99.0 else props.get("humidade"),
            "pressure_hpa": props.get("pressao"),
            "precipitation_mm": props.get("precAcumulada"),
            "radiation_kjm2": props.get("radiacao")
        })

    logger.info(f"Data normalized and transformed")

    run_inserts(config, data)
