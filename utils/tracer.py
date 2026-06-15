import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

_provider = None


def get_tracer(service_name: str = "ingestion") -> trace.Tracer:
    """
    Initialise the global TracerProvider (once) and return a named tracer.
    If OTEL_EXPORTER_OTLP_ENDPOINT is not set, traces are produced but
    not exported anywhere (no-op exporter).
    """
    global _provider

    if _provider is None:
        resource = Resource.create({"service.name": service_name})
        _provider = TracerProvider(resource=resource)

        if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
            exporter = OTLPSpanExporter()  # reads endpoint from env automatically
            _provider.add_span_processor(BatchSpanProcessor(exporter))

        trace.set_tracer_provider(_provider)

    return trace.get_tracer(service_name)


def shutdown_tracer():
    if _provider:
        _provider.shutdown()
