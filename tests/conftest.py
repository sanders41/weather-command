import os
from pathlib import Path
from shutil import copy
from unittest.mock import patch

import httpx
import pytest
from typer.testing import CliRunner

from weather_command._builder import (
    _format_date_time,
    _format_precip,
    _format_pressure,
    _format_sunrise_sunset,
    _format_wind,
    _get_units,
    _hpa_to_in,
    _mm_to_in,
    _round_to_int,
)
from weather_command._cache import Cache
from weather_command._config import Settings, append_api_key, load_settings
from weather_command._location import _build_url
from weather_command._weather import get_icon
from weather_command.models.location import Location
from weather_command.models.weather import CurrentWeather, OneCallWeather

ROOT_PATH = Path().absolute()
ASSETS_PATH = ROOT_PATH / "tests" / "assets"


@pytest.fixture(autouse=True)
def clear_lru_cache():
    yield
    append_api_key.cache_clear()
    _build_url.cache_clear()
    load_settings.cache_clear()
    get_icon.cache_clear()
    _format_date_time.cache_clear()
    _format_precip.cache_clear()
    _format_pressure.cache_clear()
    _format_sunrise_sunset.cache_clear()
    _format_wind.cache_clear()
    _get_units.cache_clear()
    _hpa_to_in.cache_clear()
    _mm_to_in.cache_clear()
    _round_to_int.cache_clear()


@pytest.fixture(autouse=True, scope="session")
def dont_write_to_home_cache_directory():
    """Makes sure a default directory is specified for cache so that the home directory is not
    written to in testing.
    """

    class ExplicitlyChooseCacheDirectory(AssertionError):
        pass

    with patch.object(
        Cache,
        "get_default_directory",
        side_effect=ExplicitlyChooseCacheDirectory,
    ):
        yield


@pytest.fixture
def mock_cache_dir(tmp_path):
    cache_path = tmp_path / "cache" / "weather-command"
    with patch.object(Cache, "get_default_directory", return_value=cache_path):
        yield cache_path


@pytest.fixture
def mock_cache_dir_with_file(tmp_path):
    cache_path = tmp_path / "cache" / "weather-command"
    if not cache_path.exists():
        cache_path.mkdir(parents=True)

    copy(str(ASSETS_PATH / "cache.json"), str(cache_path / "cache.json"))

    with patch.object(Cache, "get_default_directory", return_value=cache_path):
        yield cache_path


@pytest.fixture
def cache(tmp_path):
    yield Cache(tmp_path / "cache" / "weather-command")


@pytest.fixture
def cache_with_file(tmp_path):
    cache_path = tmp_path / "cache" / "weather-command"
    if not cache_path.exists():
        cache_path.mkdir(parents=True)

    copy(str(ASSETS_PATH / "cache.json"), str(cache_path / "cache.json"))
    yield Cache(cache_path)


@pytest.fixture(autouse=True, scope="session")
def dont_write_to_home_config_directory():
    """Makes sure a default directory is specified for config so that the home directory is not
    written to in testing.
    """

    class ExplicitlyChooseConfigDirectory(AssertionError):
        pass

    with patch.object(
        Settings,
        "get_default_directory",
        side_effect=ExplicitlyChooseConfigDirectory,
    ):
        yield


@pytest.fixture(autouse=True)
def mock_config_dir(tmp_path):
    config_path = tmp_path / "config" / "weather-command"
    if not config_path.exists():
        config_path.mkdir(parents=True)

    with patch.object(Settings, "get_default_directory", return_value=config_path):
        yield config_path


@pytest.fixture
def mock_config_dir_with_file(tmp_path):
    config_path = tmp_path / "config" / "weather-command"
    if not config_path.exists():
        config_path.mkdir(parents=True)

    copy(str(ASSETS_PATH / "weather_command.yaml"), str(config_path / "weather_command.yaml"))

    with patch.object(Cache, "get_default_directory", return_value=config_path):
        yield config_path


@pytest.fixture
def settings(tmp_path):
    config_path = tmp_path / "config" / "weather-command"
    if not config_path.exists():
        config_path.mkdir(parents=True)

    copy(str(ASSETS_PATH / "weather_command.yaml"), str(config_path / "weather_command.yaml"))
    yield load_settings(config_path)


@pytest.fixture
def settings_no_env_api_key(tmp_path, monkeypatch):
    current = os.getenv("OPEN_WEATHER_API_KEY")
    monkeypatch.delenv("OPEN_WEATHER_API_KEY", raising=False)
    config_path = tmp_path / "config" / "weather-command"
    if not config_path.exists():
        config_path.mkdir(parents=True)

    copy(str(ASSETS_PATH / "weather_command.yaml"), str(config_path / "weather_command.yaml"))
    yield load_settings(config_path)
    monkeypatch.setenv("OPEN_WEATHER_API_KEY", current)


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
        request=httpx.Request("GET", "https://localhost"),
        json=mock_current_weather_dict,
    )


@pytest.fixture
def mock_one_call_weather_dict():
    return {
        "lat": 36.1056,
        "lon": -79.7569,
        "timezone": "America/New_York",
        "timezone_offset": -14400,
        "current": {
            "dt": 1632878438,
            "sunrise": 1632827507,
            "sunset": 1632870436,
            "temp": 19.74,
            "feels_like": 19.75,
            "pressure": 1015,
            "humidity": 76,
            "dew_point": 15.39,
            "uvi": 0,
            "clouds": 6,
            "visibility": 10000,
            "wind_speed": 1.03,
            "wind_deg": 209,
            "wind_gust": 1.07,
            "weather": [{"id": 800, "main": "Clear", "description": "clear sky", "icon": "01n"}],
        },
        "minutely": [
            {"dt": 1632878460, "precipitation": 0},
            {"dt": 1632878520, "precipitation": 0},
        ],
        "hourly": [
            {
                "dt": 1632877200,
                "temp": 19.74,
                "feels_like": 19.75,
                "pressure": 1015,
                "humidity": 76,
                "dew_point": 15.39,
                "uvi": 0,
                "clouds": 6,
                "visibility": 10000,
                "wind_speed": 1.03,
                "wind_deg": 209,
                "wind_gust": 1.07,
                "weather": [
                    {"id": 800, "main": "Clear", "description": "clear sky", "icon": "01n"}
                ],
                "pop": 0,
            },
            {
                "dt": 1632880800,
                "temp": 19.76,
                "feels_like": 19.7,
                "pressure": 1015,
                "humidity": 73,
                "dew_point": 14.79,
                "uvi": 0,
                "clouds": 6,
                "visibility": 10000,
                "wind_speed": 1.04,
                "wind_deg": 233,
                "wind_gust": 1.08,
                "weather": [
                    {"id": 800, "main": "Clear", "description": "clear sky", "icon": "01n"}
                ],
                "pop": 0,
            },
            {
                "dt": 1632884400,
                "temp": 19.61,
                "feels_like": 19.45,
                "pressure": 1015,
                "humidity": 70,
                "dew_point": 13.99,
                "uvi": 0,
                "clouds": 5,
                "visibility": 10000,
                "wind_speed": 1.42,
                "wind_deg": 271,
                "wind_gust": 1.47,
                "weather": [
                    {"id": 800, "main": "Clear", "description": "clear sky", "icon": "01n"}
                ],
                "pop": 0,
            },
        ],
        "daily": [
            {
                "dt": 1632848400,
                "sunrise": 1632827507,
                "sunset": 1632870436,
                "moonrise": 1632887700,
                "moonset": 1632853200,
                "moon_phase": 0.75,
                "temp": {
                    "day": 29.18,
                    "min": 14.95,
                    "max": 29.7,
                    "night": 19.61,
                    "eve": 20.74,
                    "morn": 14.95,
                },
                "feels_like": {"day": 28.36, "night": 19.45, "eve": 20.65, "morn": 14.46},
                "pressure": 1014,
                "humidity": 35,
                "dew_point": 12.3,
                "wind_speed": 2.88,
                "wind_deg": 253,
                "wind_gust": 8.7,
                "weather": [
                    {"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}
                ],
                "clouds": 5,
                "pop": 0,
                "uvi": 5.67,
            },
            {
                "dt": 1632934800,
                "sunrise": 1632913955,
                "sunset": 1632956747,
                "moonrise": 0,
                "moonset": 1632942780,
                "moon_phase": 0.77,
                "temp": {
                    "day": 27.92,
                    "min": 17.69,
                    "max": 29.22,
                    "night": 18.78,
                    "eve": 24.18,
                    "morn": 17.69,
                },
                "feels_like": {"day": 27.88, "night": 18.62, "eve": 24.04, "morn": 17.5},
                "pressure": 1016,
                "humidity": 44,
                "dew_point": 14.51,
                "wind_speed": 3.17,
                "wind_deg": 8,
                "wind_gust": 7.44,
                "weather": [
                    {"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}
                ],
                "clouds": 0,
                "pop": 0,
                "uvi": 6.07,
            },
        ],
    }


@pytest.fixture
def mock_one_call_weather(mock_one_call_weather_dict):
    return OneCallWeather(**mock_one_call_weather_dict)


@pytest.fixture
def mock_one_call_weather_response(mock_one_call_weather_dict):
    return httpx.Response(
        200,
        request=httpx.Request("GET", "http://localhost"),
        json=mock_one_call_weather_dict,
    )


@pytest.fixture
def mock_location_dict(mock_one_call_weather_dict):
    return [
        {
            "display_name": "Greensboro, NC",
            "lat": mock_one_call_weather_dict["lat"],
            "lon": mock_one_call_weather_dict["lon"],
        }
    ]


@pytest.fixture
def mock_location(mock_location_dict):
    return Location(**mock_location_dict[0])


@pytest.fixture
def mock_location_response(mock_location_dict):
    return httpx.Response(
        200,
        request=httpx.Request("GET", "http://localhost"),
        json=mock_location_dict,
    )
