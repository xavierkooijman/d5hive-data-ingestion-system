from ingestion.connectors.sql import SQLConnector
from utils.common import resolve_secret
import logging

logger = logging.getLogger(__name__)

CONNECTORS = {
    "postgresql": SQLConnector,
    "mysql": SQLConnector,
}


def run_inserts(config, data):
    """Run insert operations for all configured destinations.
    Args:
        config (dict): The pipeline configuration containing destination details.
        data (list): A list of dictionaries representing the data to be inserted.
    """

    for dest in config["destinations"]:

        dest_config = dict(dest)

        dest_config["password"] = resolve_secret(dest_config["password"])

        logger.info(
            f"Inserting {len(data)} rows into destination: {dest['name']} into table {dest['table']}")

        destination_class = CONNECTORS.get(dest["type"])
        if not destination_class:
            logger.error(f"Unsupported destination type: {dest['type']}")
            continue

        destination = destination_class(dest_config)
        destination.insert(dest["table"], data)
