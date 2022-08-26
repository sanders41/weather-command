from datetime import datetime
from typing import List, Optional

from camel_converter.pydantic_base import CamelBase
from pydantic import Field


class Coordinates(CamelBase):
    lon: float
    lat: float


class Clouds(CamelBase):
    all: int = 0


class PrecipAmount(CamelBase):
    one_hour: float = Field(0.0, alias="1h")
    three_hour: float = Field(0.0, alias="3h")


class Weather(CamelBase):
    id: int
    main: str
    description: str
    icon: str


class Wind(CamelBase):
    speed: float = 0.0
    deg: int = 0
    gust: Optional[float] = None


class Main(CamelBase):
    temp: float = 0.0
    feels_like: float = 0.0
    temp_min: float = 0.0
    temp_max: float = 0.0
    pressure: int = 0
    humidity: int = 0


class Sys(CamelBase):
    country: str
    sunrise: datetime
    sunset: datetime


class CurrentWeather(CamelBase):
    coord: Coordinates
    weather: List[Weather]
    base: str
    main: Main
    visibility: int = 0
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
    precipitation: float = 0.0


class Hourly(CamelBase):
    dt: datetime
    temp: float = 0.0
    feels_like: float = 0.0
    pressure: int = 0
    humidity: int = 0
    dew_point: float = 0.0
    uvi: float = 0.0
    weather: List[Weather]
    clouds: int = 0
    visibility: int = 0
    wind_speed: float = 0.0
    wind_gust: float = 0.0
    wind_deg: int = 0
    rain: Optional[PrecipAmount] = None
    snow: Optional[PrecipAmount] = None
    pop: float = 0.0


class OneCallCurrent(CamelBase):
    dt: int
    sunrise: datetime
    sunset: datetime
    temp: float = 0.0
    feels_like: float = 0.0
    pressure: int = 0
    humidity: int = 0
    dew_point: float = 0
    uvi: float = 0.0
    clouds: int = 0
    visibility: int = 0
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
    pressure: int = 0
    humidity: int = 0
    dew_point: float = 0.0
    wind_speed: float = 0.0
    wind_deg: int = 0
    wind_gust: float = 0.0
    weather: List[Weather]
    clouds: int = 0
    pop: float = 0.0
    rain: float = 0.0
    uvi: float = 0.0


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
