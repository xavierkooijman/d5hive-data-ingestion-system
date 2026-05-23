from ingestion.sources.api import APIClient
from ingestion.transformations.time import normalize_unix_timestamp
from utils.common import detect_environment
from utils.destinations_executer import run_destinations
from utils.mailer import send_email
import clts_pcp as clts
import logging


def run(config):
    try:
        logger = logging.getLogger(__name__)

        tstart = clts.getts()
        logger.info("Pipeline Started")
        clts.elapt["Pipeline Started"] = clts.deltat(tstart)

        env = detect_environment()

        clts.elapt[f"Environment Detected: {env}"] = clts.deltat(tstart)

        clts.setcontext(
            f'Open-Meteo Weather Data Retrieval - Environment: {env}')

        clts.elapt[f"Fetching data from API URL: {config["source"]["base_url"]}{config["source"]["endpoint"]}"] = clts.deltat(
            tstart)

        logger.info(
            f"Fetching data from API URL: {config['source']['base_url']}{config['source']['endpoint']}")

        apiClient = APIClient(config["source"]["base_url"])
        raw_data = apiClient.get(
            config["source"]["endpoint"], params=config["source"].get("parameters", {}))

        clts.elapt["Data fetched from API"] = clts.deltat(tstart)

        clts.elapt["Normalizing and transforming data"] = clts.deltat(tstart)

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

        clts.elapt["Data normalized and transformed"] = clts.deltat(tstart)

        clts.elapt[f"Inserting data into destinations: {', '.join([dest['name'] for dest in config['destinations']])}"] = clts.deltat(
            tstart)

        run_destinations(config, data)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise
    finally:
        toemail = clts.listtimes()
        if config["email"]["send"]:
            send_email(env, config["email"], toemail)
