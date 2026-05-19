import logging
import requests
import base64
import time
import os


class LokiHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        instance_id = os.getenv("GRAFANA_INSTANCE_ID")
        api_key = os.getenv("GRAFANA_API_KEY")
        self.url = os.getenv("GRAFANA_LOKI_URL")
        self.auth = base64.b64encode(
            f"{instance_id}:{api_key}".encode()).decode()

    def emit(self, record):
        try:
            response = requests.post(
                self.url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Basic {self.auth}",
                },
                json={"streams": [{
                    "stream": {
                        "service": "ingestion",
                        "level": record.levelname,
                        "logger": record.name,
                    },
                    "values": [[str(int(time.time() * 1e9)), self.format(record)]]
                }]},
                timeout=5
            )
            print(f"Loki response: {response.status_code}")  # temp debug
        except Exception as e:
            print(f"Loki error: {e}")  # temp debug


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

        if os.getenv("GRAFANA_LOKI_URL"):
            loki_handler = LokiHandler()
            loki_handler.setFormatter(formatter)
            logger.addHandler(loki_handler)

    return logger
