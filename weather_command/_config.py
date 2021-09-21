from os import getenv

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def apppend_api_key(url: str) -> str:
    api_key = getenv("OPEN_WEATHER_API_KEY")
    return f"{url}&appid={api_key}"
