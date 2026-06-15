from ingestion.transformations.common import wind_direction_to_degrees
from ingestion.transformations.time import normalize_string_timestamp
from ingestion.pipelines.base import BaseETLPipeline
from ingestion.models.ipma import IPMARawResponse


class IPMAPipeline(BaseETLPipeline):
    def validate_raw_schema(self, data):
        IPMARawResponse.model_validate(data)
        return data

    def transform_data(self, data):
        self.logger.info(
            f"Filtering {len(data.get('features', []))} rows of data for station ID {self.config['source']['station_id']}")

        features = []
        for feature in data.get("features", []):
            if feature['properties'].get('idEstacao') == self.config["source"]["station_id"]:
                features.append(feature)

        self.logger.info(
            f"Filtered down to {len(features)} rows of data for station ID {self.config['source']['station_id']}")

        transformed_data = []
        for feature in features:
            props = feature.get("properties", {})
            coords = feature.get("geometry", {}).get(
                "coordinates", [None, None])

            transformed_data.append({
                "source": self.config["source"]["name"],
                "tstamp": normalize_string_timestamp(props.get("time"), self.config["source"]["timezone"]),
                "latitude": coords[1],
                "longitude": coords[0],
                "temperature_celsius": props.get("temperatura"),
                "wind_speed_kmh": props.get("intensidadeVentoKM"),
                "wind_direction_degrees": wind_direction_to_degrees(props.get("descDirVento")),
                "humidity_percentage": None if props.get("humidade") == -99.0 else props.get("humidade"),
                "pressure_hpa": props.get("pressao"),
                "precipitation_mm": props.get("precAcumulada"),
                "radiation_kjm2": props.get("radiacao")
            })

        return transformed_data
