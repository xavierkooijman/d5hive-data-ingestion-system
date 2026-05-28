from ingestion.sources.api import APIClient
from utils.connectors import run_inserts
import logging
from utils.common import resolve_secret
from datetime import datetime, timezone


def run(config):
    logger = logging.getLogger(__name__)

    logger.info(f"Pipeline {config['pipeline_name']} Started")

    current_timestamp = datetime.now(timezone.utc)

    params = config["source"].get("parameters", {})
    if "key" in params:
        params["key"] = resolve_secret(params["key"])

    apiClient = APIClient(config["source"]["base_url"])
    raw_data = apiClient.get(
        config["source"]["endpoint"], params=config["source"].get("parameters", {}))

    flow_segment_data = raw_data.get("flowSegmentData", {})

    logger.info(
        f"Normalizing and transforming {len(flow_segment_data.get('flowSegments', []))} rows of data")

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

    logger.info("Data normalized and transformed")

    run_inserts(config, data)
