import sys
import yaml
from dotenv import load_dotenv

from ingestion.pipelines.ipma import IPMAPipeline
from utils.logger import get_logger, shutdown_logger
from utils.common import detect_environment
from utils.mailer import send_email

load_dotenv()

PIPELINES = {
    "ipma_ingestion": IPMAPipeline,
}


def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    try:
        env = detect_environment()

        config_path = sys.argv[1]

        config = load_config(config_path)

        pipeline_name = config["pipeline_name"]

        logger = get_logger()

        pipeline = PIPELINES[pipeline_name]

        pipeline(config).run()

    except Exception as e:
        logger.error(
            f"Error occurred while running pipeline {pipeline_name}: {e}")
        send_email(config.get("email", {}),
                   f"<p>Error occurred while running pipeline {pipeline_name}: {e}</p>", env=env)

    finally:
        shutdown_logger()
