from utils.destinations_loader import load_destination
from utils.destinations_registry import get_destination
from utils.common import resolve_secret
import logging

logger = logging.getLogger(__name__)


def run_destinations(config, data):

    for dest in config["destinations"]:

        load_destination(dest["type"])

        insert_fn = get_destination(dest["type"])

        dest_config = dict(dest)

        dest_config["password"] = resolve_secret(dest_config["password"])

        logger.info(
            f"Inserting {len(data)} rows into destination: {dest['name']}")
        insert_fn(dest_config, data)
