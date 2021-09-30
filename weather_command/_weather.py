from __future__ import annotations

import sys
from enum import Enum

import httpx
from pydantic.error_wrappers import ValidationError
from rich.console import Console

from weather_command.errors import check_status_error
from weather_command.models.weather import CurrentWeather, OneCallWeather


def get_current_weather(url: str, console: Console) -> CurrentWeather:
    response = httpx.get(url)
    try:
        response.raise_for_status()
        return CurrentWeather(**response.json())
    except httpx.HTTPStatusError as e:
        check_status_error(e, console)
    except ValidationError:
        _print_validation_error(console)

    # Shouldn't be possible to reach this. Here as a fail safe.
    console.print("[red]Unable to get weather data[/red]")  # pragma: no cover
    sys.exit(1)  # pragma: no cover


def get_one_call_current_weather(url: str, console: Console) -> OneCallWeather:
    response = httpx.get(url)
    try:
        response.raise_for_status()
        return OneCallWeather(**response.json())
    except httpx.HTTPStatusError as e:
        check_status_error(e, console)
    except ValidationError:
        _print_validation_error(console)

    # Shouldn't be possible to reach this. Here as a fail safe.
    console.print("[red]Unable to get weather data[/red]")  # pragma: no cover
    sys.exit(1)  # pragma: no cover


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


def _print_validation_error(console: Console) -> None:
    console.print("[red]Unable to get the weather data for the specified location[/red]")
    sys.exit(1)
