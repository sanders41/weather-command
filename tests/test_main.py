import json
from pathlib import Path
from unittest.mock import patch

import pytest
from tomlkit import parse

from weather_command._config import LOCATION_BASE_URL
from weather_command.errors import MissingApiKey
from weather_command.main import __version__, app


def test_versions_match():
    pyproject_file = Path().absolute() / "pyproject.toml"
    with open(pyproject_file, "r") as f:
        content = f.read()
        data = parse(content)
        pyproject_version = data["tool"]["poetry"]["version"]  # type: ignore
    assert __version__ == pyproject_version


@pytest.mark.parametrize("args", [["--version"], ["-v"]])
def test_version(args, test_runner):
    result = test_runner.invoke(app, args, catch_exceptions=False)
    out = result.stdout
    assert __version__ in out


@pytest.mark.parametrize("how, city_zip", [("city", "Greensboro"), ("zip", "27405")])
@pytest.mark.parametrize("imperial", [None, "--imperial", "-i"])
@pytest.mark.parametrize(
    "state_code, state_code_flag", [(None, None), ("NC", "-s"), ("NC", "--state-code")]
)
@pytest.mark.parametrize(
    "country_code, country_code_flag", [(None, None), ("US", "-c"), ("US", "--country-code")]
)
@pytest.mark.parametrize("am_pm", [None, "--am-pm"])
@pytest.mark.parametrize(
    "forecast_type, forecast_type_flag",
    [(None, None), ("current", "--forecast-type"), ("hourly", "-f"), ("daily", "-f")],
)
@pytest.mark.parametrize("temp_only", [None, "-t", "--temp-only"])
@pytest.mark.parametrize("clear_cache", [False, True])
@pytest.mark.usefixtures("mock_cache_dir_with_file")
def test_main(
    how,
    city_zip,
    imperial,
    state_code,
    state_code_flag,
    country_code,
    country_code_flag,
    am_pm,
    forecast_type,
    forecast_type_flag,
    temp_only,
    clear_cache,
    test_runner,
    mock_current_weather_response,
    mock_one_call_weather_response,
    mock_location_response,
    cache_with_file,
):
    args = [how, city_zip, "--terminal-width", 180]

    if imperial:
        args.append(imperial)

    if state_code:
        args.append(state_code_flag)
        args.append(state_code)

    if country_code:
        args.append(country_code_flag)
        args.append(country_code)

    if am_pm:
        args.append(am_pm)

    if forecast_type:
        args.append(forecast_type_flag)
        args.append(forecast_type)

    if temp_only:
        args.append(temp_only)

    if clear_cache:
        args.append("--clear-cache")

    if forecast_type == "current" or not forecast_type:

        def mock_return(*args, **kwargs):
            if LOCATION_BASE_URL in args[0]:
                return mock_location_response

            return mock_current_weather_response

        with patch("httpx.get", side_effect=mock_return):
            result = test_runner.invoke(app, args, catch_exceptions=False)
    else:

        def mock_return(*args, **kwargs):
            if LOCATION_BASE_URL in args[0]:
                return mock_location_response

            return mock_one_call_weather_response

        with patch("httpx.get", side_effect=mock_return):
            result = test_runner.invoke(app, args, catch_exceptions=False)

    out = result.stdout

    if imperial:
        temp_unit = "F"
        wind_unit = "mph"
        precip_unit = "in"
    else:
        temp_unit = "C"
        wind_unit = "kph"
        precip_unit = "mm"

    assert "Greensboro" in out
    assert temp_unit in out

    if not temp_only:
        assert wind_unit in out

    if not temp_only and forecast_type != "daily":
        assert precip_unit in out

        if am_pm:
            assert " AM" or " PM" in out

    def load_cache():
        with open(cache_with_file._cache_file, "r") as f:
            return json.load(f)

    if clear_cache and how != "zip":
        assert not cache_with_file._cache_file.exists()
    elif clear_cache:
        assert load_cache().get("27455") is None
    else:
        assert load_cache().get("27455") is not None


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
