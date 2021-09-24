from unittest.mock import patch

import pytest

from weather_command.__main__ import app


@pytest.mark.parametrize("how, city_zip", [("city", "Greensboro"), ("zip", "27405")])
@pytest.mark.parametrize(
    "units, units_flag",
    [
        (None, None),
        ("metric", "-u"),
        ("metric", "--units"),
        ("imperial", "-u"),
        ("imperial", "--units"),
    ],
)
@pytest.mark.parametrize(
    "state_code, state_code_flag", [(None, None), ("NC", "-s"), ("NC", "--state-code")]
)
@pytest.mark.parametrize(
    "country_code, country_code_flag", [(None, None), ("US", "-c"), ("US", "--country-code")]
)
@pytest.mark.parametrize("am_pm", [None, "--am-pm"])
@pytest.mark.parametrize("temp_only", [None, "-t", "--temp-only"])
def test_current_weather_by_city(
    how,
    city_zip,
    units,
    units_flag,
    state_code,
    state_code_flag,
    country_code,
    country_code_flag,
    am_pm,
    temp_only,
    test_runner,
    mock_current_weather_response,
):
    args = [how, city_zip, "--terminal_width", 180]

    if units:
        args.append(units_flag)
        args.append(units)

    if state_code:
        args.append(state_code_flag)
        args.append(state_code)

    if country_code:
        args.append(country_code_flag)
        args.append(country_code)

    if am_pm:
        args.append(am_pm)

    if temp_only:
        args.append(temp_only)

    with patch("httpx.get", return_value=mock_current_weather_response):
        result = test_runner.invoke(app, args)

    out = result.stdout

    if units == "imperial":
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
        assert precip_unit in out

        if am_pm:
            assert " AM" in out
            assert " PM" in out


def test_missing_api_key(test_runner, monkeypatch):
    monkeypatch.delenv("OPEN_WEATHER_API_KEY", raising=False)

    result = test_runner.invoke(app, ["city", "Greensboro"])
    assert result.exit_code != 0


def test_bad_how(test_runner):
    result = test_runner.invoke(app, ["bad", "Greensboro"])
    assert result.exit_code != 0


def test_bad_units(test_runner):
    result = test_runner.invoke(app, ["city", "Greensboro", "-u", "bad"])
    assert result.exit_code != 0
