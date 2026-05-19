import logging
import logging_loki
import os


def get_logger(name):
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(module)s.%(funcName)s | %(message)s"
        )

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        loki_url = os.getenv("GRAFANA_URL")
        if loki_url:
            loki_handler = logging_loki.LokiHandler(
                url=loki_url,
                auth=(os.getenv("GRAFANA_USER"), os.getenv("GRAFANA_API_KEY")),
                tags={"app": "ingestion", "logger": name},
                version="1",
            )
            loki_handler.setFormatter(formatter)
            logger.addHandler(loki_handler)

    return logger
