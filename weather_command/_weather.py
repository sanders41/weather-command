from __future__ import annotations

from enum import Enum

import httpx

from weather_command.models.weather import CurrentWeather


def get_current_weather(url: str) -> CurrentWeather:
    response = httpx.get(url)
    response.raise_for_status()
    return CurrentWeather(**response.json())


class WeatherIcons(Enum):
    BROKEN_CLOUDS = ":sun_behind_cloud:"
    CLEAR_SKY = ":sun:"
    CLOUDS = ":cloud:"
    FEW_CLOUDS = ":sun_behind_coud:"
    HEAVY_RAIN = ":cloud_with_rain:"
    LIGHT_RAIN = ":cloud_with_rain:"
    MIST = ":cloud_with_rain:"
    MODERATE_RAIN = ":cloud_with_rain:"
    OVERCAST_CLOUDS = ":sun_behind_cloud:"
    RAIN = ":cloud_with_rain:"
    SCATTERED_CLOUDS = ":sun_behind_cloud:"
    SNOW = ":snowflake:"
    SUN = ":sun:"
    THUNDERSTORM = ":cloud_with_lightning:"

    @classmethod
    def get_icon(cls, weather_type: str) -> str | None:
        upper_weather_type = weather_type.upper().replace(" ", "_")
        try:
            return cls[upper_weather_type].value
        except KeyError:
            return None
