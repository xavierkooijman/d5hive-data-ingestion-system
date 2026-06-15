from ingestion.transformations.common import ms_to_kmh
from ingestion.transformations.time import normalize_unix_timestamp
from ingestion.pipelines.base import BaseETLPipeline
from ingestion.models.openweathermap import OpenWeatherMapRawResponse


class OpenWeatherMapPipeline(BaseETLPipeline):
    def validate_raw_schema(self, data):
        OpenWeatherMapRawResponse.model_validate(data)
        return data

    def transform_data(self, data):
        coordinates = data.get("coord", {})
        current_weather = data.get("main", {})
        wind = data.get("wind", {})

        transformed_data = [{
            "source": self.config["source"]["name"],
            "tstamp": normalize_unix_timestamp(data.get("dt")),
            "latitude": coordinates.get("lat"),
            "longitude": coordinates.get("lon"),
            "temperature_celsius": current_weather.get("temp"),
            "wind_speed_kmh": ms_to_kmh(wind.get("speed")),
            "wind_direction_degrees": wind.get("deg"),
            "wind_gust_kmh": ms_to_kmh(wind.get("gust")),
            "sea_level_pressure_hpa": current_weather.get("sea_level"),
            "ground_level_pressure_hpa": current_weather.get("grnd_level"),
            "humidity_percentage": current_weather.get("humidity"),
            "cloudiness_percentage": data.get("clouds", {}).get("all"),
            "visibility_meters": data.get("visibility"),
            "precipitation_mm": data.get("rain", {}).get("1h", 0)
        }]

        return transformed_data
