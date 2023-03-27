from datetime import datetime
from os import getenv
from unittest.mock import Mock, patch

import httpx
import pytest

from weather_command import _builder
from weather_command._cache import CacheItem
from weather_command._config import WEATHER_BASE_URL
from weather_command._utils import build_weather_url
from weather_command.models.weather import PrecipAmount, Wind

UNITS = ("metric", "imperial")


@pytest.mark.parametrize("units", UNITS)
@pytest.mark.parametrize("am_pm", [False, True])
@pytest.mark.parametrize("rain", [None, PrecipAmount(one_hour=0.1, three_hour=0.3)])  # type: ignore
@pytest.mark.parametrize("snow", [None, PrecipAmount(one_hour=0.1, three_hour=0.3)])  # type: ignore
@pytest.mark.parametrize("wind", [None, Wind(speed=1.2, deg=23, gust=2.1)])
def test_current_weather_all(mock_current_weather, units, am_pm, rain, snow, wind, mock_location):
    if mock_current_weather.rain and not rain:
        mock_current_weather.rain = None

    if rain:
        mock_current_weather.rain = rain

    if mock_current_weather.snow and not snow:
        mock_current_weather.snow = None

    if snow:
        mock_current_weather.snow = snow

    mock_current_weather.wind = wind

    table = _builder.current_weather_all(mock_current_weather, units, am_pm, mock_location)
    assert len(table.columns) == 12
    assert table.row_count == 1


@pytest.mark.parametrize("units", UNITS)
def test_current_weather_temp(
    mock_current_weather,
    units,
    mock_location,
):
    table = _builder._current_weather_temp(mock_current_weather, units, mock_location)
    assert len(table.columns) == 2
    assert table.row_count == 1


@patch("weather_command._builder.get_location_details")
@patch("weather_command._cache.Cache.get")
@pytest.mark.usefixtures("mock_cache_dir")
async def test_current_weather_no_cache_hit(
    mock_cache_get_call,
    mock_location_details_call,
    mock_current_weather_response,
    mock_location,
    monkeypatch,
):
    async def mock_get_weather_response(*args, **kwargs):
        return mock_current_weather_response

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get_weather_response)
    mock_cache_get_call.return_value = CacheItem()
    mock_location_details_call.return_value = mock_location
    await _builder.show_current("zip", "27455")
    assert mock_cache_get_call.called_once()
    assert mock_location_details_call.called_once()


@pytest.mark.parametrize("pager", [True, False])
@pytest.mark.parametrize("temp_only", [True, False])
@pytest.mark.usefixtures("mock_cache_dir_with_file")
@patch("weather_command._cache.datetime")
async def test_current_weather_cache_hit(mock_dt, temp_only, pager, capfd):
    mock_dt.utcnow = Mock(return_value=datetime(2021, 12, 22, 1, 36, 38))
    await _builder.show_current("zip", "27455", temp_only=temp_only, pager=pager)
    out, _ = capfd.readouterr()
    assert "Greensboro" in out


@pytest.mark.parametrize("units", UNITS)
@pytest.mark.parametrize("am_pm", [False, True])
@pytest.mark.parametrize("wind", [None, 1.2])
@pytest.mark.parametrize("pressure", [None, 1000])
def test_daily_all(mock_one_call_weather, mock_location, units, am_pm, wind, pressure):
    mock_one_call_weather.daily[0].wind_speed = wind
    mock_one_call_weather.daily[0].wind_gust = wind
    mock_one_call_weather.daily[0].pressure = pressure

    table = _builder.daily_all(
        weather=mock_one_call_weather, units=units, am_pm=am_pm, location=mock_location
    )
    assert len(table.columns) == 14
    assert table.row_count == len(mock_one_call_weather.daily)


@pytest.mark.parametrize("units", UNITS)
@pytest.mark.parametrize("am_pm", [False, True])
def test_daily_temp_only(mock_one_call_weather, mock_location, units, am_pm):
    table = _builder._daily_temp_only(
        weather=mock_one_call_weather, units=units, am_pm=am_pm, location=mock_location
    )
    assert len(table.columns) == 3
    assert table.row_count == len(mock_one_call_weather.daily)


@patch("weather_command._builder.get_location_details")
@patch("weather_command._cache.Cache.get")
@pytest.mark.usefixtures("mock_cache_dir")
async def test_show_daily_no_cache_hit(
    mock_cache_get_call,
    mock_location_details_call,
    mock_one_call_weather_response,
    mock_location,
    monkeypatch,
):
    async def mock_get_weather_response(*args, **kwargs):
        return mock_one_call_weather_response

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get_weather_response)

    mock_cache_get_call.return_value = CacheItem()
    mock_location_details_call.return_value = mock_location
    await _builder.show_daily("zip", "27455")
    assert mock_cache_get_call.called_once()
    assert mock_location_details_call.called_once()


@pytest.mark.parametrize("pager", [True, False])
@pytest.mark.parametrize("temp_only", [True, False])
@pytest.mark.usefixtures("mock_cache_dir_with_file")
@patch("weather_command._cache.datetime")
async def test_show_daily_cache_hit(mock_dt, temp_only, pager, capfd):
    mock_dt.utcnow = Mock(return_value=datetime(2021, 12, 22, 1, 36, 38))
    await _builder.show_daily("zip", "27455", temp_only=temp_only, pager=pager)
    out, _ = capfd.readouterr()
    assert "Greensboro" in out


@pytest.mark.parametrize("units", UNITS)
@pytest.mark.parametrize("am_pm", [False, True])
@pytest.mark.parametrize("rain", [None, PrecipAmount(one_hour=0.1, three_hour=0.0)])  # type: ignore
@pytest.mark.parametrize("snow", [None, PrecipAmount(one_hour=0.1, three_hour=0.0)])  # type: ignore
@pytest.mark.parametrize("wind", [None, 1.2])
@pytest.mark.parametrize("gust", [None, 2.1])
@pytest.mark.parametrize("pressure", [None, 1000])
def test_hourly_all(
    mock_one_call_weather, mock_location, units, am_pm, rain, snow, wind, gust, pressure
):
    if mock_one_call_weather.hourly[0].rain and not rain:
        mock_one_call_weather.hourly[0].rain = None

    if rain:
        mock_one_call_weather.hourly[0].rain = rain

    if mock_one_call_weather.hourly[0].snow and not snow:
        mock_one_call_weather.hourly[0].snow = None

    if mock_one_call_weather.hourly[0].snow and not snow:
        mock_one_call_weather.hourly[0].snow = None

    if snow:
        mock_one_call_weather.hourly[0].snow = snow

    mock_one_call_weather.hourly[0].wind_speed = wind
    mock_one_call_weather.hourly[0].wind_gust = gust
    mock_one_call_weather.hourly[0].pressure = pressure

    table = _builder.hourly_all(
        weather=mock_one_call_weather, units=units, am_pm=am_pm, location=mock_location
    )
    assert len(table.columns) == 14
    assert table.row_count == len(mock_one_call_weather.hourly)


@pytest.mark.parametrize("units", UNITS)
@pytest.mark.parametrize("am_pm", [False, True])
def test_hourly_temp_only(mock_one_call_weather, mock_location, units, am_pm):
    table = _builder._hourly_temp_only(
        weather=mock_one_call_weather, units=units, am_pm=am_pm, location=mock_location
    )
    assert len(table.columns) == 3
    assert table.row_count == len(mock_one_call_weather.hourly)


@patch("weather_command._builder.get_location_details")
@patch("weather_command._cache.Cache.get")
@pytest.mark.usefixtures("mock_cache_dir")
async def test_show_hourly_no_cache_hit(
    mock_cache_get_call,
    mock_location_details_call,
    mock_one_call_weather_response,
    mock_location,
    monkeypatch,
):
    async def mock_get_weather_response(*args, **kwargs):
        return mock_one_call_weather_response

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get_weather_response)

    mock_cache_get_call.return_value = CacheItem()
    mock_location_details_call.return_value = mock_location
    await _builder.show_hourly("zip", "27455")
    assert mock_cache_get_call.called_once()
    assert mock_location_details_call.called_once()


@pytest.mark.parametrize("pager", [True, False])
@pytest.mark.parametrize("temp_only", [True, False])
@pytest.mark.usefixtures("mock_cache_dir_with_file")
@patch("weather_command._cache.datetime")
async def test_show_hourly_cache_hit(mock_dt, temp_only, pager, capfd):
    mock_dt.utcnow = Mock(return_value=datetime(2021, 12, 22, 1, 36, 38))
    await _builder.show_hourly("zip", "27455", temp_only=temp_only, pager=pager)
    out, _ = capfd.readouterr()
    assert "Greensboro" in out


@pytest.mark.parametrize("units", ["metric", "imperial"])
def test_build_url_current(units):
    lon = 0.123
    lat = 789.1
    got = build_weather_url(
        forecast_type="current",
        units=units,
        lon=lon,
        lat=lat,
    )

    assert got.startswith(WEATHER_BASE_URL)
    assert "/weather?" in got
    assert f"&units={units}" in got
    assert f"lon={lon}" in got
    assert f"lat={lat}" in got
    assert f"&appid={getenv('OPEN_WEATHER_API_KEY')}" in got


@pytest.mark.parametrize("units", ["metric", "imperial"])
@pytest.mark.parametrize("forecast_type", ["hourly", "daily", "alert"])
def test_build_url_one_one_call(units, forecast_type):
    lon = 0.123
    lat = 789.1
    got = build_weather_url(forecast_type=forecast_type, units=units, lon=lon, lat=lat)

    assert got.startswith(WEATHER_BASE_URL)
    assert "/onecall?" in got
    assert f"units={units}" in got
    assert f"lon={lon}" in got
    assert f"lat={lat}" in got
    assert f"&appid={getenv('OPEN_WEATHER_API_KEY')}" in got


@pytest.mark.usefixtures("settings")
def test_build_url_current_api_key_env_and_settings():
    lon = 0.123
    lat = 789.1
    got = build_weather_url(
        forecast_type="current",
        units="metric",
        lon=lon,
        lat=lat,
    )

    assert got.startswith(WEATHER_BASE_URL)
    assert "/weather?" in got
    assert "&units=metric" in got
    assert f"lon={lon}" in got
    assert f"lat={lat}" in got
    assert f"&appid={getenv('OPEN_WEATHER_API_KEY')}" in got


def test_build_url_current_api_key_settings(settings_no_env_api_key, monkeypatch):
    monkeypatch.delenv("OPEN_WEATHER_API_KEY", raising=False)
    lon = 0.123
    lat = 789.1
    got = build_weather_url(
        forecast_type="current",
        units="metric",
        lon=lon,
        lat=lat,
    )

    assert got.startswith(WEATHER_BASE_URL)
    assert "/weather?" in got
    assert "&units=metric" in got
    assert f"lon={lon}" in got
    assert f"lat={lat}" in got
    assert f"&appid={settings_no_env_api_key.api_key_file}" in got


def test_hpa_to_in():
    assert _builder._hpa_to_in(1000) == 29.53


def test_kph_to_mph():
    # Rounding to account for imprecision in floating point numbers. As long as this is accurate to
    # 2 digits that is good enough.
    assert round(_builder._kph_to_mph(1), 2) == 0.62


def test_mm_to_in():
    assert _builder._mm_to_in(1) == 0.04


@pytest.mark.parametrize(
    "units, expected",
    [("metric", ("mm", "hPa", "kph", "C")), ("imperial", ("in", "in", "mph", "F"))],
)
def test_get_units(units, expected):
    assert _builder._get_units(units) == expected


def test_get_units_error():
    with pytest.raises(ValueError):
        _builder._get_units("bad")
