from pydantic import BaseModel, ConfigDict


class OpenMeteoCurrentWeather(BaseModel):
    time: int
    interval: float
    temperature: float
    windspeed: float
    winddirection: float
    is_day: int
    weathercode: int
    model_config = ConfigDict(extra="allow")


class OpenMeteoRawResponse(BaseModel):
    latitude: float
    longitude: float
    generationtime_ms: float
    utc_offset_seconds: int
    timezone: str
    timezone_abbreviation: str
    elevation: float
    current_weather: OpenMeteoCurrentWeather
    model_config = ConfigDict(extra="allow")
