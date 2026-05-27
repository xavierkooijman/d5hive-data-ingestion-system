from ingestion.connectors.sql import SQLDestination
from utils.common import resolve_secret
import logging

logger = logging.getLogger(__name__)

DESTINATIONS = {
    "postgresql": SQLDestination,
    "mysql": SQLDestination,
}


def run_destinations(config, data):

    for dest in config["destinations"]:

        dest_config = dict(dest)

        dest_config["password"] = resolve_secret(dest_config["password"])

        logger.info(
            f"Inserting {len(data)} rows into destination: {dest['name']} into table {dest['table']}")

        destination_class = DESTINATIONS.get(dest["type"])
        if not destination_class:
            logger.error(f"Unsupported destination type: {dest['type']}")
            continue

        destination = destination_class(dest_config)
        destination.insert(dest["table"], data)
