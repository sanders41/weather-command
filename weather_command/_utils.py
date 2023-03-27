from __future__ import annotations

from weather_command._config import WEATHER_BASE_URL, append_api_key


def build_weather_url(
    forecast_type: str,
    units: str,
    lon: float | None = None,
    lat: float | None = None,
) -> str:
    if forecast_type == "current":
        url = f"{WEATHER_BASE_URL}/weather?lat={lat}&lon={lon}&units={units}"
    else:
        url = f"{WEATHER_BASE_URL}/onecall?lat={lat}&lon={lon}&units={units}"

    return append_api_key(url)
