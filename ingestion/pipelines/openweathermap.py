from ingestion.sources.api import APIClient
from ingestion.transformations.common import ms_to_kmh
from ingestion.transformations.time import normalize_unix_timestamp
from utils.common import detect_environment
from utils.connectors import run_inserts
from utils.mailer import send_email
import logging
from utils.common import resolve_secret


def run(config):
    try:
        logger = logging.getLogger(__name__)

        logger.info("Pipeline Started")

        env = detect_environment()

        params = config["source"].get("parameters", {})
        if "appid" in params:
            params["appid"] = resolve_secret(params["appid"])

        logger.info(
            f"Fetching data from API URL: {config['source']['base_url']}{config['source']['endpoint']}")

        apiClient = APIClient(config["source"]["base_url"])
        raw_data = apiClient.get(
            config["source"]["endpoint"], params=config["source"].get("parameters", {}))

        coordinates = raw_data.get("coord", {})
        current_weather = raw_data.get("main", {})
        wind = raw_data.get("wind", {})

        data = [{
            "hostfeed": "hostfeed",
            "source": config["source"]["name"],
            "tstamp": normalize_unix_timestamp(raw_data.get("dt")),
            "latitude": coordinates.get("lat"),
            "longitude": coordinates.get("lon"),
            "temperature_celsius": current_weather.get("temp"),
            "wind_speed_kmh": ms_to_kmh(wind.get("speed")),
            "wind_direction_degrees": wind.get("deg"),
            "wind_gust_kmh": ms_to_kmh(wind.get("gust")),
            "sea_level_pressure_hpa": current_weather.get("sea_level"),
            "ground_level_pressure_hpa": current_weather.get("grnd_level"),
            "humidity_percentage": current_weather.get("humidity"),
            "cloudiness_percentage": raw_data.get("clouds", {}).get("all"),
            "visibility_meters": raw_data.get("visibility"),
            "precipitation_mm": raw_data.get("rain", {}).get("1h", 0)
        }]

        run_inserts(config, data)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise
    finally:
        toemail = ""
        if config["email"]["send"]:
            send_email(env, config["email"], toemail)
