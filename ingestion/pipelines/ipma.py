from ingestion.sources.api import APIClient
from ingestion.transformations.common import wind_direction_to_degrees
from ingestion.transformations.time import normalize_string_timestamp
from utils.common import detect_environment
from utils.destinations_executer import run_destinations
from utils.mailer import send_email
import clts_pcp as clts
import logging


def run(config):
    try:
        logger = logging.getLogger(__name__)

        tstart = clts.getts()
        clts.elapt["Pipeline Started"] = clts.deltat(tstart)
        logger.info("Starting IPMA Weather Station Data Retrieval pipeline")

        env = detect_environment()

        clts.elapt[f"Environment Detected: {env}"] = clts.deltat(tstart)
        logger.info(f"Environment detected: {env}")

        clts.setcontext(
            f'IPMA Weather Station Data Retrieval - Environment: {env}')

        clts.elapt[f"Fetching data from API URL: {config["source"]["base_url"]}"] = clts.deltat(
            tstart)
        logger.info(
            f"Fetching data from API URL: {config['source']['base_url']}{config['source']['endpoint']}")

        apiClient = APIClient(config["source"]["base_url"])
        raw_data = apiClient.get(config["source"]["endpoint"])

        logger.info(
            f"{len(raw_data.get('features', []))} rows of data fetched successfully from API")

        clts.elapt["Data fetched from API"] = clts.deltat(tstart)

        clts.elapt["Normalizing and transforming data"] = clts.deltat(tstart)
        logger.info("Normalizing and transforming data")

        features = []
        for feature in raw_data.get("features", []):
            if feature['properties'].get('idEstacao') == config["source"]["station_id"]:
                features.append(feature)

        data = []

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

        logger.info("Data normalized and transformed")
        clts.elapt["Data normalized and transformed"] = clts.deltat(tstart)

        logger.info(
            f"Inserting {len(data)} rows into destinations: {', '.join([dest['name'] for dest in config['destinations']])}")
        clts.elapt[f"Inserting {len(data)} rows into destinations: {', '.join([dest['name'] for dest in config['destinations']])}"] = clts.deltat(
            tstart)

        run_destinations(config, data)
    except Exception as e:
        logger.error(f"Pipeline {config['pipeline_name']} failed: {e}")
        raise
    finally:
        toemail = clts.listtimes()
        if config["email"]["send"]:
            logger.info("Sending email notification")
            send_email(env, config["email"], toemail)
            logger.info("Email notification sent")
