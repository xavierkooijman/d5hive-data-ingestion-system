from datetime import datetime, timezone
from ingestion.pipelines.base import BaseETLPipeline


class TrafficFlowPipeline(BaseETLPipeline):
    def validate_data(self, data):
        return data

    def transform_data(self, data):
        flow_segment_data = data.get("flowSegmentData", {})

        transformed_data = [{
            "hostfeed": "hostfeed",
            "source": self.config["source"]["name"],
            "tstamp": datetime.now(timezone.utc),
            "latitude": self.config["source"]["parameters"].get("point", "").split(",")[0],
            "longitude": self.config["source"]["parameters"].get("point", "").split(",")[1],
            "current_speed_kmh": flow_segment_data.get("currentSpeed"),
            "free_flow_speed_kmh": flow_segment_data.get("freeFlowSpeed"),
            "current_travel_time_s": flow_segment_data.get("currentTravelTime"),
            "free_flow_travel_time_s": flow_segment_data.get("freeFlowTravelTime"),
            "confidence": flow_segment_data.get("confidence"),
            "road_closure": flow_segment_data.get("roadClosure"),
            "geometry": flow_segment_data.get("coordinates")
        }]

        return transformed_data
