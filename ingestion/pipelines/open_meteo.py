from ingestion.sources.api import APIClient
from ingestion.transformations.time import normalize_unix_timestamp
from utils.connectors import run_inserts
import logging


def run(config):
    logger = logging.getLogger(__name__)

    logger.info(f"Pipeline {config['pipeline_name']} Started")

    logger.info(
        f"Fetching data from API URL: {config['source']['base_url']}{config['source']['endpoint']}")

    apiClient = APIClient(config["source"]["base_url"])
    raw_data = apiClient.get(
        config["source"]["endpoint"], params=config["source"].get("parameters", {}))

    logger.info("Normalizing and transforming data")

    current_weather = raw_data.get("current_weather", {})

    data = [{
        "hostfeed": "hostfeed",
        "source": config["source"]["name"],
        "tstamp": normalize_unix_timestamp(current_weather.get("time")),
        "latitude": raw_data.get("latitude"),
        "longitude": raw_data.get("longitude"),
        "temperature_celsius": current_weather.get("temperature"),
        "wind_speed_kmh": current_weather.get("windspeed"),
        "wind_direction_degrees": current_weather.get("winddirection"),
    }]

    logger.info("Data normalized and transformed")
    run_inserts(config, data)
