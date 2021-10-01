from os import getenv

import pytest

from weather_command import _builder
from weather_command._config import WEATHER_BASE_URL

UNITS = ("metric", "imperial")


@pytest.mark.parametrize("units", UNITS)
@pytest.mark.parametrize("am_pm", [False, True])
def test_current_weather_all(mock_current_weather, units, am_pm):
    table = _builder._current_weather_all(mock_current_weather, units, am_pm)
    assert len(table.columns) == 12
    assert table.row_count == 1


@pytest.mark.parametrize("units", UNITS)
def test_current_weather_temp(mock_current_weather, units):
    table = _builder._current_weather_temp(mock_current_weather, units)
    assert len(table.columns) == 2
    assert table.row_count == 1


@pytest.mark.parametrize("units", UNITS)
@pytest.mark.parametrize("am_pm", [False, True])
def test_daily_all(mock_one_call_weather, mock_location, units, am_pm):
    table = _builder._daily_all(
        weather=mock_one_call_weather, units=units, am_pm=am_pm, location=mock_location
    )
    assert len(table.columns) == 13
    assert table.row_count == len(mock_one_call_weather.daily)


@pytest.mark.parametrize("units", UNITS)
@pytest.mark.parametrize("am_pm", [False, True])
def test_daily_temp_only(mock_one_call_weather, mock_location, units, am_pm):
    table = _builder._daily_temp_only(
        weather=mock_one_call_weather, units=units, am_pm=am_pm, location=mock_location
    )
    assert len(table.columns) == 4
    assert table.row_count == len(mock_one_call_weather.daily)


@pytest.mark.parametrize("units", UNITS)
@pytest.mark.parametrize("am_pm", [False, True])
def test_hourly_all(mock_one_call_weather, mock_location, units, am_pm):
    table = _builder._hourly_all(
        weather=mock_one_call_weather, units=units, am_pm=am_pm, location=mock_location
    )
    assert len(table.columns) == 12
    assert table.row_count == len(mock_one_call_weather.hourly)


@pytest.mark.parametrize("units", UNITS)
@pytest.mark.parametrize("am_pm", [False, True])
def test_hourly_temp_only(mock_one_call_weather, mock_location, units, am_pm):
    table = _builder._hourly_temp_only(
        weather=mock_one_call_weather, units=units, am_pm=am_pm, location=mock_location
    )
    assert len(table.columns) == 3
    assert table.row_count == len(mock_one_call_weather.hourly)


@pytest.mark.parametrize("how, city_zip", [("city", "Greensboro"), ("zip", "27405")])
@pytest.mark.parametrize("units", ["metric", "imperial"])
@pytest.mark.parametrize("state_code", ["NC", None])
@pytest.mark.parametrize("country_code", ["US", None])
def test_build_url_current(how, city_zip, units, state_code, country_code):
    got = _builder._build_url(
        forecast_type="current",
        how=how,
        city_zip=city_zip,
        units=units,
        state_code=state_code,
        country_code=country_code,
    )

    assert got.startswith(WEATHER_BASE_URL)

    if how == "city":
        assert f"weather?q={city_zip}" in got
    else:
        assert f"weather?zip={city_zip}" in got

    assert f"&units={units}" in got

    if state_code:
        assert f"&state_code={state_code}" in got
    else:
        assert f"&state_code={state_code}" not in got

    if country_code:
        assert f"&country_code={country_code}" in got
    else:
        assert f"&country_code={country_code}" not in got

    assert f"&appid={getenv('OPEN_WEATHER_API_KEY')}" in got


@pytest.mark.parametrize("units", ["metric", "imperial"])
@pytest.mark.parametrize("forecast_type", ["hourly", "daily", "alert"])
def test_build_url_one_one_call(units, forecast_type):
    lon = 0.123
    lat = 789.1
    got = _builder._build_url(forecast_type=forecast_type, units=units, lon=lon, lat=lat)

    assert got.startswith(WEATHER_BASE_URL)

    assert f"units={units}" in got
    assert f"lon={lon}" in got
    assert f"lat={lat}" in got
    assert f"&appid={getenv('OPEN_WEATHER_API_KEY')}" in got


@pytest.mark.parametrize("units, expected", [("metric", "mm"), ("imperial", "in")])
def test_precip_units(units, expected):
    assert _builder._precip_units(units) == expected


def test_precip_units_error():
    with pytest.raises(ValueError):
        _builder._precip_units("bad")


@pytest.mark.parametrize("units, expected", [("metric", "kph"), ("imperial", "mph")])
def test_speed_units(units, expected):
    assert _builder._speed_units(units) == expected


def test_speed_units_error():
    with pytest.raises(ValueError):
        _builder._speed_units("bad")


@pytest.mark.parametrize("units, expected", [("metric", "C"), ("imperial", "F")])
def test_temp_units(units, expected):
    assert _builder._temp_units(units) == expected


def test_temp_units_error():
    with pytest.raises(ValueError):
        _builder._speed_units("bad")
