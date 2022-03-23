import io

import pytest
from httpx import AsyncClient
from rich.console import Console

from weather_command._config import LOCATION_BASE_URL
from weather_command._tui import (
    CurrentWeather,
    DailyWeather,
    HourlyWeather,
    WeatherHeader,
    _generate_title,
)


def render(renderable) -> str:
    console = Console(file=io.StringIO(), width=100)
    console.print(renderable)
    return console.file.getvalue()  # type: ignore


def test_generate_title_am_pm(mock_location):
    result = _generate_title(mock_location, True)

    assert mock_location.display_name in result
    assert "AM" or "PM" in result


def test_generate_title_24_hour(mock_location):
    result = _generate_title(mock_location, False)

    assert mock_location.display_name in result
    assert "AM" and "PM" not in result


@pytest.mark.usefixtures("mock_cache_dir_with_file")
async def test_current_weather_imperial(
    mock_location_response, mock_location, mock_current_weather_response, monkeypatch
):
    async def mock_get_response(*args, **kwargs):
        if LOCATION_BASE_URL in args[1]:
            return mock_location_response

        return mock_current_weather_response

    monkeypatch.setattr(AsyncClient, "get", mock_get_response)
    weather = CurrentWeather(mock_location, "zip", "27455", "imperial", True)

    await weather.on_mount()
    panel = weather.render()
    rendered = render(panel)

    assert "Current Weather" in rendered
    assert "(F)" in rendered
    assert "AM" or "PM" in rendered


@pytest.mark.usefixtures("mock_cache_dir_with_file")
async def test_current_weather_metric(
    mock_location_response, mock_location, mock_current_weather_response, monkeypatch
):
    async def mock_get_response(*args, **kwargs):
        if LOCATION_BASE_URL in args[1]:
            return mock_location_response

        return mock_current_weather_response

    monkeypatch.setattr(AsyncClient, "get", mock_get_response)
    weather = CurrentWeather(mock_location, "zip", "27455", "metric", False)

    await weather.on_mount()
    panel = weather.render()
    rendered = render(panel)

    assert "Current Weather" in rendered
    assert "(C)" in rendered
    assert "AM" and "PM" not in rendered


@pytest.mark.usefixtures("mock_cache_dir_with_file")
async def test_current_weather_cache(
    mock_location_response, mock_location, mock_current_weather_response, monkeypatch
):
    async def mock_get_response(*args, **kwargs):
        if LOCATION_BASE_URL in args[1]:
            return mock_location_response

        return mock_current_weather_response

    monkeypatch.setattr(AsyncClient, "get", mock_get_response)
    weather = CurrentWeather(mock_location, "zip", "27455", "metric", False)

    # Initial load. First time cache is set
    await weather.on_mount()
    assert weather.panel_cache is not None

    # Reload using cache
    await weather.build_panel()
    assert weather.panel_cache is not None

    # Clear cache
    weather.clear_cache()
    assert weather.panel_cache is None


@pytest.mark.usefixtures("mock_cache_dir_with_file")
async def test_daily_weather_imperial(
    mock_location_response, mock_location, mock_one_call_weather_response, monkeypatch
):
    async def mock_get_response(*args, **kwargs):
        if LOCATION_BASE_URL in args[1]:
            return mock_location_response

        return mock_one_call_weather_response

    monkeypatch.setattr(AsyncClient, "get", mock_get_response)
    header = DailyWeather(mock_location, "zip", "27455", "imperial", True)

    await header.on_mount()
    panel = header.render()
    rendered = render(panel)

    assert "Daily Weather" in rendered
    assert "(F)" in rendered
    assert "AM" or "PM" in rendered


@pytest.mark.usefixtures("mock_cache_dir_with_file")
async def test_daily_weather_metric(
    mock_location_response, mock_location, mock_one_call_weather_response, monkeypatch
):
    async def mock_get_response(*args, **kwargs):
        if LOCATION_BASE_URL in args[1]:
            return mock_location_response

        return mock_one_call_weather_response

    monkeypatch.setattr(AsyncClient, "get", mock_get_response)
    weather = DailyWeather(mock_location, "zip", "27455", "metric", False)

    await weather.on_mount()
    panel = weather.render()
    rendered = render(panel)

    assert "Daily Weather" in rendered
    assert "(C)" in rendered
    assert "AM" and "PM" not in rendered


@pytest.mark.usefixtures("mock_cache_dir_with_file")
async def test_daily_weather_cache(
    mock_location_response, mock_location, mock_one_call_weather_response, monkeypatch
):
    async def mock_get_response(*args, **kwargs):
        if LOCATION_BASE_URL in args[1]:
            return mock_location_response

        return mock_one_call_weather_response

    monkeypatch.setattr(AsyncClient, "get", mock_get_response)
    weather = DailyWeather(mock_location, "zip", "27455", "metric", False)

    # Initial load. First time cache is set
    await weather.on_mount()
    assert weather.panel_cache is not None

    # Reload using cache
    await weather.build_panel()
    assert weather.panel_cache is not None

    # Clear cache
    weather.clear_cache()
    assert weather.panel_cache is None


@pytest.mark.usefixtures("mock_cache_dir_with_file")
async def test_hourly_weather_imperial(
    mock_location_response, mock_location, mock_one_call_weather_response, monkeypatch
):
    async def mock_get_response(*args, **kwargs):
        if LOCATION_BASE_URL in args[1]:
            return mock_location_response

        return mock_one_call_weather_response

    monkeypatch.setattr(AsyncClient, "get", mock_get_response)
    weather = HourlyWeather(mock_location, "zip", "27455", "imperial", True)

    await weather.on_mount()
    panel = weather.render()
    rendered = render(panel)

    assert "Hourly Weather" in rendered
    assert "(F)" in rendered
    assert "AM" or "PM" in rendered


@pytest.mark.usefixtures("mock_cache_dir_with_file")
async def test_hourly_weather_metric(
    mock_location_response, mock_location, mock_one_call_weather_response, monkeypatch
):
    async def mock_get_response(*args, **kwargs):
        if LOCATION_BASE_URL in args[1]:
            return mock_location_response

        return mock_one_call_weather_response

    monkeypatch.setattr(AsyncClient, "get", mock_get_response)
    weather = HourlyWeather(mock_location, "zip", "27455", "metric", False)

    await weather.on_mount()
    panel = weather.render()
    rendered = render(panel)

    assert "Hourly Weather" in rendered
    assert "(C)" in rendered
    assert "AM" and "PM" not in rendered


@pytest.mark.usefixtures("mock_cache_dir_with_file")
async def test_hourly_weather_cache(
    mock_location_response, mock_location, mock_one_call_weather_response, monkeypatch
):
    async def mock_get_response(*args, **kwargs):
        if LOCATION_BASE_URL in args[1]:
            return mock_location_response

        return mock_one_call_weather_response

    monkeypatch.setattr(AsyncClient, "get", mock_get_response)
    weather = HourlyWeather(mock_location, "zip", "27455", "metric", False)

    # Initial load. First time cache is set
    await weather.on_mount()
    assert weather.panel_cache is not None

    # Reload using cache
    await weather.build_panel()
    assert weather.panel_cache is not None

    # Clear cache
    weather.clear_cache()
    assert weather.panel_cache is None


def test_weather_header_icon():
    header = WeatherHeader()
    rendered = render(header.render())
    assert "🌞" in rendered
