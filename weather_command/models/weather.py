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
    one_hour: Optional[float] = Field(None, alias="1h")
    three_hour: Optional[float] = Field(None, alias="3h")


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


class Minutely(CamelBase):
    dt: datetime
    precipitation: float


class Hourly(CamelBase):
    dt: datetime
    temp: float
    feels_like: float
    pressure: int
    humidity: int
    dew_point: float
    uvi: float
    clouds: int
    visibility: int
    wind_speed: float
    wind_gust: float
    wind_deg: int
    rain: Optional[float] = None
    snow: Optional[float] = None
    pop: int


class OneCallCurrent(CamelBase):
    dt: int
    sunrise: datetime
    sunset: datetime
    temp: float
    feels_like: float
    pressure: int
    humidity: int
    dew_point: float
    uvi: float
    clouds: int
    visibility: int
    wind_speed: float = 0.0
    wind_deg: int = 0
    wind_gust: float = 0.0
    weather: List[Weather]


class Temp(CamelBase):
    day: float = 0.0
    min: float = 0.0
    max: float = 0.0
    night: float = 0.0
    eve: float = 0.0
    morn: float = 0.0


class Daily(CamelBase):
    dt: datetime
    sunrise: datetime
    sunset: datetime
    moonrise: datetime
    moonset: datetime
    moon_phase: float
    temp: Temp
    feels_like: Temp
    pressure: int
    humidity: int
    dew_point: float
    wind_speed: float = 0.0
    wind_deg: int = 0
    wind_gust: float = 0.0
    weather: List[Weather]
    clouds: int
    pop: int
    uvi: float


class Alert(CamelBase):
    sender_name: str
    event: str
    start: datetime
    end: datetime
    description: str
    tags: List[str]


class OneCallWeather(CamelBase):
    lat: float
    lon: float
    timezone: str
    timezone_offset: int
    current: OneCallCurrent
    minutely: Optional[List[Minutely]] = None
    hourly: List[Hourly]
    daily: List[Daily]
