import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import httpx
import pytest
import yaml

from weather_command.errors import MissingApiKey
from weather_command.main import __version__, app

if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib


def test_versions_match():
    pyproject_file = Path().absolute() / "pyproject.toml"
    with open(pyproject_file, "rb") as f:
        data = tomllib.load(f)
        pyproject_version = data["tool"]["poetry"]["version"]
    assert __version__ == pyproject_version


@pytest.mark.parametrize("args", [["--version"], ["-v"]])
def test_version(args, test_runner):
    result = test_runner.invoke(app, args, catch_exceptions=False)
    out = result.stdout
    assert __version__ in out


@pytest.mark.parametrize("how, city_zip", [("city", "Greensboro"), ("zip", "27405")])
@pytest.mark.usefixtures("mock_cache_dir_with_file")
def test_main_default_params(
    how,
    city_zip,
    test_runner,
    mock_current_weather_response,
    mock_one_call_weather_response,
    mock_location_response,
    cache_with_file,
    monkeypatch,
):
    def mock_get_location_response(*args, **kwargs):
        return mock_location_response

    async def mock_get_weather_response(*args, **kwargs):
        if "onecall" in args[1]:
            return mock_one_call_weather_response

        return mock_current_weather_response

    monkeypatch.setattr(httpx, "get", mock_get_location_response)
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get_weather_response)
    args = [how, city_zip, "--terminal-width", 180]
    result = test_runner.invoke(app, args, catch_exceptions=False)

    out = result.stdout

    assert "Greensboro" in out
    assert "C" in out
    assert "kph" in out
    assert "mm" in out

    def load_cache():
        with open(cache_with_file._cache_file) as f:
            return json.load(f)

    assert (
        load_cache().get(
            "https://nominatim.openstreetmap.org/search?format=json&limit=1&postalcode=27455"
        )
        is not None
    )


@pytest.mark.usefixtures("mock_cache_dir")
@patch("weather_command._cache.datetime")
def test_main_cache_hit(
    mock_dt,
    mock_location,
    mock_current_weather,
    mock_one_call_weather,
    test_runner,
    cache_with_file,
):
    mock_dt.now = Mock(return_value=datetime(2021, 12, 22, 1, 36, 38, tzinfo=timezone.utc))
    location = mock_location
    current_weather = mock_current_weather
    one_call_weather = mock_one_call_weather

    cache_key = "https://nominatim.openstreetmap.org/search?format=json&limit=1&postalcode=27455"

    cache_with_file.add(
        cache_key=cache_key,
        location=location,
        current_weather=current_weather,
        one_call_weather=one_call_weather,
    )
    args = ["zip", "27455", "--terminal-width", 180]
    result = test_runner.invoke(app, args, catch_exceptions=False)

    out = result.stdout

    assert "Greensboro" in out


@pytest.mark.usefixtures("mock_cache_dir_with_file")
def test_main_cache_hit_expired(
    mock_one_call_weather_response, mock_current_weather_response, test_runner, monkeypatch
):
    async def mock_get_weather_response(*args, **kwargs):
        if "onecall" in args[1]:
            return mock_one_call_weather_response

        return mock_current_weather_response

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get_weather_response)
    args = ["zip", "27455", "--terminal-width", 180]
    result = test_runner.invoke(app, args, catch_exceptions=False)

    out = result.stdout

    assert "Greensboro" in out


@pytest.mark.parametrize("imperial", ["--imperial", "-i"])
@pytest.mark.parametrize("state_code_flag", ["-s", "--state-code"])
@pytest.mark.parametrize("country_code_flag", ["-c", "--country-code"])
@pytest.mark.parametrize(
    "forecast_type, forecast_type_flag",
    [("current", "--forecast-type"), ("hourly", "-f"), ("daily", "-f")],
)
@pytest.mark.parametrize("temp_only", ["-t", "--temp-only"])
@pytest.mark.parametrize("clear_cache", [True, False])
@pytest.mark.usefixtures("mock_cache_dir_with_file")
def test_main_with_params(
    imperial,
    state_code_flag,
    country_code_flag,
    forecast_type,
    forecast_type_flag,
    temp_only,
    clear_cache,
    test_runner,
    mock_current_weather_response,
    mock_one_call_weather_response,
    mock_location_response,
    monkeypatch,
):
    def mock_get_location_response(*args, **kwargs):
        return mock_location_response

    async def mock_get_weather_response(*args, **kwargs):
        if "onecall" in args[1]:
            return mock_one_call_weather_response

        return mock_current_weather_response

    monkeypatch.setattr(httpx, "get", mock_get_location_response)
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get_weather_response)

    args = [
        "zip",
        "27455",
        "--am-pm",
        imperial,
        state_code_flag,
        "NC",
        country_code_flag,
        "USA",
        "--am-pm",
        forecast_type_flag,
        forecast_type,
        temp_only,
        "--terminal-width",
        180,
    ]

    if clear_cache:
        args.append("--clear-cache")

    if forecast_type == "current" or not forecast_type:
        result = test_runner.invoke(app, args, catch_exceptions=False)
    else:
        result = test_runner.invoke(app, args, catch_exceptions=False)

    out = result.stdout

    assert "Greensboro" in out
    assert "F" in out

    if not temp_only:
        assert "mph" in out

    if not temp_only and forecast_type != "daily":
        assert "in" in out

    assert " AM" or " PM" in out


@pytest.mark.parametrize("how, city_zip", [("city", "Greensboro"), ("zip", "27405")])
@pytest.mark.usefixtures("mock_cache_dir")
def test_main_from_settings_params(
    how,
    city_zip,
    test_runner,
    mock_current_weather_response,
    mock_one_call_weather_response,
    mock_location_response,
    monkeypatch,
    mock_config_dir,
):
    def mock_get_location_response(*args, **kwargs):
        return mock_location_response

    async def mock_get_weather_response(*args, **kwargs):
        if "onecall" in args[1]:
            return mock_one_call_weather_response

        return mock_current_weather_response

    monkeypatch.setattr(httpx, "get", mock_get_location_response)
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get_weather_response)
    settings = {"settings": {"api_key": "file", "units": "imperial", "time_format": "am/pm"}}

    with open(mock_config_dir / "weather_command.yaml", "w") as f:
        yaml.safe_dump(settings, f)

    args = [how, city_zip, "--terminal-width", 180]
    result = test_runner.invoke(app, args, catch_exceptions=False)

    out = result.stdout

    assert "Greensboro" in out
    assert "F" in out
    assert "mph" in out
    assert " AM" or " PM" in out


@pytest.mark.parametrize("how, city_zip", [("city", "Greensboro"), ("zip", "27405")])
@pytest.mark.usefixtures("mock_cache_dir", "mock_config_dir_with_file")
def test_main_from_settings_params_temp_only(
    how,
    city_zip,
    test_runner,
    mock_current_weather_response,
    mock_one_call_weather_response,
    mock_location_response,
    monkeypatch,
):
    def mock_get_location_response(*args, **kwargs):
        return mock_location_response

    async def mock_get_weather_response(*args, **kwargs):
        if "onecall" in args[1]:
            return mock_one_call_weather_response

        return mock_current_weather_response

    monkeypatch.setattr(httpx, "get", mock_get_location_response)
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get_weather_response)
    args = [how, city_zip, "--terminal-width", 180]
    result = test_runner.invoke(app, args, catch_exceptions=False)

    out = result.stdout

    assert "Greensboro" in out
    assert "F" in out


@pytest.mark.usefixtures("mock_cache_dir")
def test_missing_api_key(test_runner, monkeypatch):
    monkeypatch.delenv("OPEN_WEATHER_API_KEY", raising=False)

    with pytest.raises(MissingApiKey):
        test_runner.invoke(app, ["city", "Greensboro"], catch_exceptions=False)


@pytest.mark.usefixtures("mock_cache_dir")
def test_bad_how(test_runner):
    result = test_runner.invoke(app, ["bad", "Greensboro"])
    assert result.exit_code > 1


@pytest.mark.usefixtures("mock_cache_dir")
def test_bad_forecast_type(test_runner):
    result = test_runner.invoke(app, ["city", "Greensboro", "-f", "bad"])
    assert result.exit_code > 1
