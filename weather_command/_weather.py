from __future__ import annotations

from enum import Enum

import httpx

from weather_command.models.current_weather import CurrentWeather


def get_current_weather(url: str) -> CurrentWeather:
    response = httpx.get(url)
    response.raise_for_status()
    return CurrentWeather(**response.json())


class WeatherIcons(Enum):
    CLOUDS = ":cloud:"
    MIST = ":cloud_with_rain:"
    RAIN = ":cloud_with_rain:"
    SUN = ":sun:"

    @classmethod
    def get_value(cls, weather_type: str) -> str | None:
        upper_weather_type = weather_type.upper()
        try:
            return cls[upper_weather_type].value
        except KeyError:
            return None
