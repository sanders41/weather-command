import httpx
import pytest
from typer.testing import CliRunner

from weather_command.models.weather import CurrentWeather


@pytest.fixture(autouse=True)
def env_vars(monkeypatch):
    monkeypatch.setenv("OPEN_WEATHER_API_KEY", "test")
    yield
    monkeypatch.delenv("OPEN_WEATHER_API_KEY", raising=False)


@pytest.fixture
def test_runner():
    return CliRunner()


@pytest.fixture
def mock_current_weather_dict():
    return {
        "coord": {"lon": -79.792, "lat": 36.0726},
        "weather": [
            {
                "id": 211,
                "main": "Thunderstorm",
                "description": "thunderstorm",
                "icon": "11d",
            },
            {"id": 701, "main": "Mist", "description": "mist", "icon": "50d"},
            {
                "id": 500,
                "main": "Rain",
                "description": "light rain",
                "icon": "10d",
            },
        ],
        "base": "stations",
        "main": {
            "temp": 296.92,
            "feels_like": 297.42,
            "temp_min": 295.27,
            "temp_max": 298.64,
            "pressure": 1009,
            "humidity": 79,
        },
        "visibility": 4828,
        "wind": {"speed": 0.45, "deg": 275, "gust": 3.58},
        "rain": {"1h": 0.55},
        "clouds": {"all": 90},
        "dt": 1632345032,
        "sys": {
            "type": 2,
            "id": 2003175,
            "country": "US",
            "sunrise": 1632308836,
            "sunset": 1632352582,
        },
        "timezone": -14400,
        "id": 4469146,
        "name": "Greensboro",
        "cod": 200,
    }


@pytest.fixture
def mock_current_weather(mock_current_weather_dict):
    return CurrentWeather(**mock_current_weather_dict)


@pytest.fixture
def mock_current_weather_response(mock_current_weather_dict):
    return httpx.Response(
        200,
        request=httpx.request("GET", "https://fakeurl.com"),
        json=mock_current_weather_dict,
    )
