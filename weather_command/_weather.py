from __future__ import annotations

import sys
from enum import Enum

import httpx
from pydantic.error_wrappers import ValidationError
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed

from weather_command._config import console
from weather_command.errors import check_status_error
from weather_command.models.weather import CurrentWeather, OneCallWeather


@retry(stop=stop_after_attempt(5), wait=wait_fixed(0.5), reraise=True)
def get_current_weather(url: str) -> CurrentWeather:
    response = httpx.get(url)
    try:
        response.raise_for_status()
        current_weather = CurrentWeather(**response.json())
    except httpx.HTTPStatusError as e:
        check_status_error(e, console)
    except ValidationError:
        _print_validation_error()

    return current_weather


@retry(stop=stop_after_attempt(5), wait=wait_fixed(0.5), reraise=True)
def get_one_call_current_weather(url: str) -> OneCallWeather:
    response = httpx.get(url)
    try:
        response.raise_for_status()
        one_call_weather = OneCallWeather(**response.json())
    except httpx.HTTPStatusError as e:
        check_status_error(e, console)
    except ValidationError:
        _print_validation_error()

    return one_call_weather


class WeatherIcons(Enum):
    BROKEN_CLOUDS = ":sun_behind_cloud:"
    CLEAR_SKY = ":sun:"
    CLOUDS = ":cloud:"
    FEW_CLOUDS = ":sun_behind_cloud:"
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


def _print_validation_error() -> None:
    console.print("Unable to get the weather data for the specified location", style="error")
    sys.exit(1)
