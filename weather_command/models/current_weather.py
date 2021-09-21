from datetime import datetime
from typing import List, Optional

from camel_converter.pydantic_base import CamelBase
from pydantic import Field


class Coordinates(CamelBase):
    lon: float
    lat: float


class Clouds(CamelBase):
    all: int


class PrecipAmount(CamelBase):
    one_hour: Optional[int] = Field(None, alias="1h")
    three_hour: Optional[int] = Field(None, alias="3h")


class Weather(CamelBase):
    id: int
    main: str
    description: str
    icon: str


class Wind(CamelBase):
    speed: float
    deg: int
    gust: Optional[float] = None


class Main(CamelBase):
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int


class Sys(CamelBase):
    type: int
    id: int
    country: str
    sunrise: datetime
    sunset: datetime


class CurrentWeather(CamelBase):
    coord: Coordinates
    weather: List[Weather]
    base: str
    main: Main
    visibility: int
    wind: Optional[Wind] = None
    clouds: Optional[Clouds] = None
    rain: Optional[PrecipAmount] = None
    snow: Optional[PrecipAmount] = None
    dt: datetime
    sys: Sys
    timezone: int
    id: int
    name: str
    cod: int
