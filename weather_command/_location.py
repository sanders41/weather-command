from __future__ import annotations

import sys
from functools import lru_cache

import httpx
from pydantic.error_wrappers import ValidationError
from tenacity import retry
from tenacity.retry import retry_if_exception_type, retry_unless_exception_type
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed

from weather_command._cache import Cache
from weather_command._config import LOCATION_BASE_URL, console
from weather_command.errors import UnknownSearchTypeError, check_status_error
from weather_command.models.location import Location


@retry(
    retry=(retry_if_exception_type() & retry_unless_exception_type(UnknownSearchTypeError)),
    stop=stop_after_attempt(5),
    wait=wait_fixed(0.5),
    reraise=True,
)
def get_location_details(
    *,
    how: str,
    city_zip: str,
    state: str | None = None,
    country: str | None = None,
) -> Location:
    if how not in ("city", "zip"):
        raise UnknownSearchTypeError(f"{type} is not a valid type")

    cache = Cache()

    base_url = build_location_url(how, city_zip, state, country)
    cache_hit = cache.get(base_url)
    if cache_hit and cache_hit.location:
        return cache_hit.location

    response = httpx.get(base_url, headers={"user-agent": "weather-command"})
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        check_status_error(e, console)

    if not response.json():
        _print_location_not_found_error()
        sys.exit(1)

    response_json = response.json()

    try:
        # Sometimes the response comes back as a single location and sometimes it is a list of
        # locations. The if/else here is to handle both of these cases.
        if isinstance(response_json, list):
            location = Location(**response_json[0])
        else:
            location = Location(**response_json)

        cache.add(cache_key=base_url, location=location)
    except ValidationError:
        _print_location_not_found_error()
        sys.exit(1)

    return location


@lru_cache(maxsize=1)
def build_location_url(how: str, city_zip: str, state: str | None, country: str | None) -> str:
    """Cache so if retries are needed the url only needs to be built once."""
    if how == "zip":
        base_url = f"{LOCATION_BASE_URL}&postalcode={city_zip}"
    else:
        base_url = f"{LOCATION_BASE_URL}&city={city_zip}"

    if state:
        base_url = f"{base_url}&state={state}"

    if country:
        base_url = f"{base_url}&country={country}"

    return base_url


def _print_location_not_found_error() -> None:
    console.print("[red]Unable to get information for the specified location.[/red]")
