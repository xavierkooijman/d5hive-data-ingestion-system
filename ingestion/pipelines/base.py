from ingestion.sources.api import APIClient
from utils.common import detect_environment, resolve_secret
from ingestion.sources.api import APIClient
from utils.connectors import run_inserts
import logging
from abc import ABC, abstractmethod


class BaseETLPipeline(ABC):
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    def extract_data(self):
        api_client = APIClient(self.config["source"]["base_url"])
        return api_client.get(self.config["source"]["endpoint"], params=self.config["source"].get("parameters", {}), headers=self.config["source"].get("headers", {}))

    @abstractmethod
    def validate_data(self, data):
        pass

    @abstractmethod
    def transform_data(self, data):
        pass

    def load_data(self, transformed_data):
        run_inserts(self.config, transformed_data)

    def run(self):
        self.logger.info(f"Pipeline {self.config['pipeline_name']} Started")
        data = self.extract_data()
        validated_data = self.validate_data(data)
        self.logger.info("Normalizing and transforming data")
        transformed_data = self.transform_data(validated_data)
        self.logger.info("Data normalized and transformed")
        self.load_data(transformed_data)
        self.logger.info(
            f"Pipeline {self.config['pipeline_name']} completed successfully")
