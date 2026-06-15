from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class OpenWeatherMapCoord(BaseModel):
    lon: float
    lat: float
    model_config = ConfigDict(extra="allow")


class OpenWeatherMapMain(BaseModel):
    temp: float
    feels_like: float
    pressure: int
    humidity: int
    sea_level: int
    grnd_level: int
    model_config = ConfigDict(extra="allow")


class OpenWeatherMapWind(BaseModel):
    speed: float
    deg: int
    gust: float
    model_config = ConfigDict(extra="allow")


class OpenWeatherMapClouds(BaseModel):
    all: int
    model_config = ConfigDict(extra="allow")


class OpenWeatherMapRain(BaseModel):
    one_h: float = Field(alias="1h")
    model_config = ConfigDict(extra="allow")


class OpenWeatherMapRawResponse(BaseModel):
    coord: OpenWeatherMapCoord
    main: OpenWeatherMapMain
    visibility: int
    wind: OpenWeatherMapWind
    clouds: OpenWeatherMapClouds
    rain: Optional[OpenWeatherMapRain] = None
    dt: int
    model_config = ConfigDict(extra="allow")
