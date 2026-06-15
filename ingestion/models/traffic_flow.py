from pydantic import BaseModel, ConfigDict


class TrafficFlowCoordinate(BaseModel):
    latitude: float
    longitude: float
    model_config = ConfigDict(extra="allow")


class TrafficFlowRawResponse(BaseModel):
    currentSpeed: float
    freeFlowSpeed: float
    currentTravelTime: float
    freeFlowTravelTime: float
    confidence: float
    roadClosure: bool
    coordinate: list[TrafficFlowCoordinate]
    model_config = ConfigDict(extra="allow")
