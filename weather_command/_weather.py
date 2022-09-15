from __future__ import annotations

import sys
from enum import Enum
from functools import lru_cache

import httpx
from httpx import AsyncClient
from pydantic.error_wrappers import ValidationError
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed

from weather_command._cache import Cache
from weather_command._config import console
from weather_command.errors import check_status_error
from weather_command.models.weather import CurrentWeather, OneCallWeather


@retry(stop=stop_after_attempt(5), wait=wait_fixed(0.5), reraise=True)
async def get_current_weather(url: str, how: str, city_zip: str) -> CurrentWeather:
    try:
        async with AsyncClient() as client:
            response = await client.get(url)

        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        check_status_error(e, console)

    try:
        weather = CurrentWeather(**response.json())
    except ValidationError:
        _print_validation_error()

    if how == "zip":
        cache = Cache()
        cache.add(city_zip=city_zip, current_weather=weather)
    return weather


@retry(stop=stop_after_attempt(5), wait=wait_fixed(0.5), reraise=True)
async def get_one_call_weather(url: str, how: str, city_zip: str) -> OneCallWeather:
    async with AsyncClient() as client:
        response = await client.get(url)
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        check_status_error(e, console)

    try:
        weather = OneCallWeather(**response.json())
    except ValidationError:
        _print_validation_error()

    if how == "zip":
        cache = Cache()
        cache.add(city_zip=city_zip, one_call_weather=weather)

    return weather


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
    VERY_HEAVY_RAIN = ":cloud_with_rain:"


@lru_cache(maxsize=32)
def get_icon(weather_type: str) -> str | None:
    upper_weather_type = weather_type.upper().replace(" ", "_")
    try:
        return WeatherIcons[upper_weather_type].value
    except KeyError:
        return None


def _print_validation_error() -> None:
    console.print("Unable to get the weather data for the specified location", style="error")
    sys.exit(1)
