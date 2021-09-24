from os import getenv

BASE_URL = "https://api.openweathermap.org/data/2.5"


class MissingApiKey(Exception):
    pass


def apppend_api_key(url: str) -> str:
    api_key = getenv("OPEN_WEATHER_API_KEY")
    if not api_key:
        raise MissingApiKey(
            "An environment variable named OPEN_WEATHER_API_KEY containing the API key is required"
        )

    return f"{url}&appid={api_key}"
