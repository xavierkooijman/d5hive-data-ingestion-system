import logging
import os
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggingHandler

_provider = None


def get_logger():
    global _provider
    logger = logging.getLogger()

    if any(isinstance(h, LoggingHandler) for h in logger.handlers):
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    logger.addHandler(handler)

    if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        resource = Resource.create({"service.name": "ingestion"})

        _provider = LoggerProvider(resource=resource)

        exporter = OTLPLogExporter()
        _provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

        otel_handler = LoggingHandler(logger_provider=_provider)

        logger.addHandler(otel_handler)

    return logger


def shutdown_logger():
    if _provider:
        _provider.shutdown()
