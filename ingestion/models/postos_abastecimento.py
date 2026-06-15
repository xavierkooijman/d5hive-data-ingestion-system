from pydantic import BaseModel, ConfigDict
from typing import Literal


class PostosAbastecimentoGeometry(BaseModel):
    type: Literal["Point"]
    coordinates: list[float]
    model_config = ConfigDict(extra="allow")


class PostosAbastecimentoFeatureProperties(BaseModel):
    Marca: str
    Latitude__Y_: float
    Longitude__X_: float
    globalid: str
    model_config = ConfigDict(extra="allow")


class PostosAbastecimentoFeature(BaseModel):
    type: Literal["Feature"]
    geometry: PostosAbastecimentoGeometry
    properties: PostosAbastecimentoFeatureProperties
    model_config = ConfigDict(extra="allow")


class PostosAbastecimentoRawResponse(BaseModel):
    type: Literal["FeatureCollection"]
    features: list[PostosAbastecimentoFeature]
    model_config = ConfigDict(extra="allow")
