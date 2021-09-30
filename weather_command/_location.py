from __future__ import annotations

import httpx

from weather_command._config import LOCATION_BASE_URL
from weather_command.errors import UnknownSearchTypeError
from weather_command.models.location import Location


def get_location_details(
    *, how: str, city_zip: str, state: str | None = None, country: str | None = None
) -> Location:
    if how not in ["city", "zip"]:
        raise UnknownSearchTypeError(f"{type} is not a valid type")

    if how == "city":
        base_url = f"{LOCATION_BASE_URL}&city={city_zip}"
    elif how == "zip":
        base_url = f"{LOCATION_BASE_URL}&postalcode={city_zip}"

    if state:
        base_url = f"{base_url}&state={state}"

    if country:
        base_url = f"{base_url}&country={country}"

    response = httpx.get(base_url, headers={"user-agent": "weather-command"})
    response.raise_for_status()
    response_json = response.json()

    if isinstance(response_json, list):
        return Location(**response_json[0])

    return Location(**response_json)
