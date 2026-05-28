from ingestion.sources.api import APIClient
from ingestion.transformations.time import normalize_unix_timestamp
from utils.common import detect_environment
from utils.connectors import run_inserts
from utils.mailer import send_email
import logging


def run(config):
    try:
        logger = logging.getLogger(__name__)

        logger.info("Pipeline Started")

        env = detect_environment()

        logger.info(
            f"Fetching data from API URL: {config['source']['base_url']}{config['source']['endpoint']}")

        apiClient = APIClient(config["source"]["base_url"])
        raw_data = apiClient.get(
            config["source"]["endpoint"], params=config["source"].get("parameters", {}))

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

        run_inserts(config, data)
    except Exception as e:
        logger.error(f"Pipeline {config['pipeline_name']} failed: {e}")
        raise
    finally:
        toemail = ""
        if config["email"]["send"]:
            send_email(env, config["email"], toemail)
