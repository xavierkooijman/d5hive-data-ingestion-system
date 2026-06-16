from datetime import datetime, timezone
from ingestion.models.traffic_flow import TrafficFlowRawResponse
from ingestion.pipelines.base import BaseETLPipeline
import json


class TrafficFlowPipeline(BaseETLPipeline):
    def validate_raw_schema(self, data):
        TrafficFlowRawResponse.model_validate(data)
        return data

    def transform_data(self, data):
        flow_segment_data = data.get("flowSegmentData", {})

        transformed_data = [{
            "source": self.config["source"]["name"],
            "frc": flow_segment_data.get("frc"),
            "tstamp": datetime.now(timezone.utc),
            "latitude": self.config["source"]["parameters"].get("point", "").split(",")[0],
            "longitude": self.config["source"]["parameters"].get("point", "").split(",")[1],
            "current_speed_kmh": flow_segment_data.get("currentSpeed"),
            "free_flow_speed_kmh": flow_segment_data.get("freeFlowSpeed"),
            "current_travel_time_s": flow_segment_data.get("currentTravelTime"),
            "free_flow_travel_time_s": flow_segment_data.get("freeFlowTravelTime"),
            "confidence": flow_segment_data.get("confidence"),
            "road_closure": flow_segment_data.get("roadClosure"),
            "flow_segment_geometry": json.dumps(flow_segment_data.get("coordinates"))
        }]

        return transformed_data
