from pydantic import BaseModel, ConfigDict


class TrafficFlowCoordinate(BaseModel):
    latitude: float
    longitude: float
    model_config = ConfigDict(extra="allow")


class TrafficFlowCoordinates(BaseModel):
    coordinate: list[TrafficFlowCoordinate]
    model_config = ConfigDict(extra="allow")


class TrafficFlowSegmentData(BaseModel):
    currentSpeed: float
    freeFlowSpeed: float
    currentTravelTime: float
    freeFlowTravelTime: float
    confidence: float
    roadClosure: bool
    coordinates: TrafficFlowCoordinates
    model_config = ConfigDict(extra="allow")


class TrafficFlowRawResponse(BaseModel):
    flowSegmentData: TrafficFlowSegmentData
    model_config = ConfigDict(extra="allow")
