from __future__ import annotations

from functools import lru_cache
from os import getenv

from rich.console import Console
from rich.theme import Theme

from weather_command.errors import MissingApiKey

WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
LOCATION_BASE_URL = "https://nominatim.openstreetmap.org/search?format=json&limit=1"


@lru_cache(maxsize=16)
def append_api_key(url: str) -> str:
    api_key = getenv("OPEN_WEATHER_API_KEY")
    if not api_key:
        raise MissingApiKey(
            "An environment variable named OPEN_WEATHER_API_KEY containing the API key is required"
        )

    return f"{url}&appid={api_key}"


custom_style = Theme({"error": "red", "date": "green"})
console = Console(theme=custom_style)
