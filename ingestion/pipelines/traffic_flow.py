from ingestion.sources.api import fetch_data_from_api
from utils.common import detect_environment
from utils.destinations_executer import run_destinations
from utils.email import send_email
import clts_pcp as clts
import logging
from utils.common import resolve_secret
from datetime import datetime


def run(config):
    try:
        logger = logging.getLogger(__name__)

        tstart = clts.getts()
        logger.info("Pipeline Started")
        clts.elapt["Pipeline Started"] = clts.deltat(tstart)

        env = detect_environment()

        clts.elapt[f"Environment Detected: {env}"] = clts.deltat(tstart)

        clts.setcontext(
            f'TomTom Traffic Flow Data Retrieval - Environment: {env}')

        current_timestamp = datetime.now().isoformat()

        clts.elapt[f"Fetching data from API URL: {config["source"]["url"]}"] = clts.deltat(
            tstart)

        params = config["source"].get("parameters", {})
        if "key" in params:
            params["key"] = resolve_secret(params["key"])

        raw_data = fetch_data_from_api(
            config["source"]["url"], params=params)

        clts.elapt["Data fetched from API"] = clts.deltat(tstart)

        clts.elapt["Normalizing and transforming data"] = clts.deltat(tstart)

        flow_segment_data = raw_data.get("flowSegmentData", {})

        data = [{
            "hostfeed": "hostfeed",
            "source": config["source"]["name"],
            "tstamp": current_timestamp,
            "latitude": config["source"]["parameters"].get("point", "").split(",")[0],
            "longitude": config["source"]["parameters"].get("point", "").split(",")[1],
            "current_speed_kmh": flow_segment_data.get("currentSpeed"),
            "free_flow_speed_kmh": flow_segment_data.get("freeFlowSpeed"),
            "current_travel_time_s": flow_segment_data.get("currentTravelTime"),
            "free_flow_travel_time_s": flow_segment_data.get("freeFlowTravelTime"),
            "confidence": flow_segment_data.get("confidence"),
            "road_closure": flow_segment_data.get("roadClosure"),
            "geometry": flow_segment_data.get("coordinates")
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
