from pydantic import BaseModel, ConfigDict
from typing import Literal


class IPMAGeometry(BaseModel):
    type: Literal["Point"]
    coordinates: list[float]


class IPMAFeatureProperties(BaseModel):
    intensidadeVentoKM: float
    temperatura: float
    idEstacao: int
    pressao: float
    humidade: float
    precAcumulada: float
    radiacao: float
    time: str
    descDirVento: str
    model_config = ConfigDict(extra="allow")


class IPMAFeature(BaseModel):
    type: Literal["Feature"]
    geometry: IPMAGeometry
    properties: IPMAFeatureProperties
    model_config = ConfigDict(extra="allow")


class IPMARawResponse(BaseModel):
    type: Literal["FeatureCollection"]
    features: list[IPMAFeature]
    model_config = ConfigDict(extra="allow")
