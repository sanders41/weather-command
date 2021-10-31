from unittest.mock import patch

import pytest

from weather_command._config import LOCATION_BASE_URL
from weather_command.errors import MissingApiKey
from weather_command.main import app


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
    test_runner,
    mock_current_weather_response,
    mock_one_call_weather_response,
    mock_location_response,
):
    args = [how, city_zip, "--terminal_width", 180]

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


def test_missing_api_key(test_runner, monkeypatch):
    monkeypatch.delenv("OPEN_WEATHER_API_KEY", raising=False)

    with pytest.raises(MissingApiKey):
        test_runner.invoke(app, ["city", "Greensboro"], catch_exceptions=False)


def test_bad_how(test_runner):
    result = test_runner.invoke(app, ["bad", "Greensboro"])
    assert result.exit_code > 1


def test_bad_forecast_type(test_runner):
    result = test_runner.invoke(app, ["city", "Greensboro", "-f", "bad"])
    assert result.exit_code > 1
