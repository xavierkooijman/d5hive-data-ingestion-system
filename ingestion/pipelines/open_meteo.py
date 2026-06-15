from ingestion.transformations.time import normalize_unix_timestamp
from ingestion.pipelines.base import BaseETLPipeline
from ingestion.models.open_meteo import OpenMeteoRawResponse


class OpenMeteoPipeline(BaseETLPipeline):
    def validate_raw_schema(self, data):
        OpenMeteoRawResponse.model_validate(data)
        return data

    def transform_data(self, data):
        current_weather = data.get("current_weather", {})

        transformed_data = [{
            "source": self.config["source"]["name"],
            "tstamp": normalize_unix_timestamp(current_weather.get("time")),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "temperature_celsius": current_weather.get("temperature"),
            "wind_speed_kmh": current_weather.get("windspeed"),
            "wind_direction_degrees": current_weather.get("winddirection"),
        }]

        return transformed_data
