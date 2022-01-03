from __future__ import annotations

import sys
from enum import Enum

import httpx
from pydantic.error_wrappers import ValidationError
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed

from weather_command._cache import Cache
from weather_command._config import console
from weather_command.errors import check_status_error
from weather_command.models.weather import CurrentWeather, OneCallWeather


@retry(stop=stop_after_attempt(5), wait=wait_fixed(0.5), reraise=True)
def get_current_weather(url: str, how: str, city_zip: str) -> CurrentWeather:
    try:
        response = httpx.get(url)
        response.raise_for_status()
        weather = CurrentWeather(**response.json())
        if how == "zip":
            cache = Cache()
            cache.add(city_zip=city_zip, current_weather=weather)
        return weather
    except httpx.HTTPStatusError as e:
        check_status_error(e, console)
    except ValidationError:
        _print_validation_error()

    # Make mypy happy
    raise  # pragma: no cover


@retry(stop=stop_after_attempt(5), wait=wait_fixed(0.5), reraise=True)
def get_one_call_current_weather(url: str, how: str, city_zip: str) -> OneCallWeather:
    response = httpx.get(url)
    try:
        response.raise_for_status()
        weather = OneCallWeather(**response.json())
        if how == "zip":
            cache = Cache()
            cache.add(city_zip=city_zip, one_call_weather=weather)
        return weather
    except httpx.HTTPStatusError as e:
        check_status_error(e, console)
    except ValidationError:
        _print_validation_error()

    # Make mypy happy
    raise  # pragma: no cover


class WeatherIcons(Enum):
    BROKEN_CLOUDS = ":sun_behind_cloud:"
    CLEAR_SKY = ":sun:"
    CLOUDS = ":cloud:"
    FEW_CLOUDS = ":sun_behind_cloud:"
    HEAVY_RAIN = ":cloud_with_rain:"
    HEAVY_INTENSITY_RAIN = ":cloud_with_rain:"
    LIGHT_RAIN = ":cloud_with_rain:"
    LIGHT_SNOW = ":snowflake:"
    MIST = ":cloud_with_rain:"
    MODERATE_RAIN = ":cloud_with_rain:"
    MODERATE_SNOW = ":snowflake:"
    OVERCAST_CLOUDS = ":sun_behind_cloud:"
    RAIN = ":cloud_with_rain:"
    RAIN_AND_SNOW = ":cloud_with_rain: :snowflake:"
    SCATTERED_CLOUDS = ":sun_behind_cloud:"
    SNOW = ":snowflake:"
    HEAVY_SNOW = ":snowflake:"
    HEAVY_INTENSITY_SNOW = ":snowflake:"
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
