import pytest
from httpx import AsyncClient, HTTPStatusError, Request, Response
from rich._emoji_codes import EMOJI

from weather_command._weather import (
    WeatherIcons,
    get_current_weather,
    get_icon,
    get_one_call_weather,
)


@pytest.mark.parametrize(
    "condition, expected",
    [("Sun", ":sun:"), ("broken clouds", ":sun_behind_cloud:"), ("none", None)],
)
def test_get_icon(condition, expected):
    icon = get_icon(condition)
    assert icon == expected


@pytest.mark.parametrize("icon", [x.value for x in WeatherIcons])
def test_icons(icon):
    icons = icon.split(" ")
    for icon in icons:
        assert icon.replace(":", "") in list(EMOJI.keys())


async def test_current_weather_http_error_404(capfd, monkeypatch):
    async def mock_get_response(*args, **kwargs):
        return Response(404, request=Request("get", url="https://test.com"))

    monkeypatch.setattr(AsyncClient, "get", mock_get_response)

    with pytest.raises(SystemExit):
        await get_current_weather(url="https://test.com", how="city", city_zip="test")

    out, _ = capfd.readouterr()
    assert "Unable" in out


async def test_get_current_weather_https_error(monkeypatch):
    async def mock_get_response(*args, **kwargs):
        return Response(500, request=Request("get", url="https://test.com"))

    monkeypatch.setattr(AsyncClient, "get", mock_get_response)

    with pytest.raises(HTTPStatusError):
        await get_current_weather(url="https://test.com", how="city", city_zip="test")


async def test_get_current_weather_validation_error(capfd, monkeypatch):
    async def mock_get_response(*args, **kwargs):
        return Response(200, request=Request("get", url="https://test.com"), json={"bad": None})

    monkeypatch.setattr(AsyncClient, "get", mock_get_response)

    with pytest.raises(SystemExit):
        await get_current_weather(url="https://test.com", how="city", city_zip="test")

    out, _ = capfd.readouterr()
    assert "Unable" in out


async def test_one_call_current_weather_http_error_404(capfd, monkeypatch):
    async def mock_get_response(*args, **kwargs):
        return Response(404, request=Request("get", url="https://test.com"))

    monkeypatch.setattr(AsyncClient, "get", mock_get_response)

    with pytest.raises(SystemExit):
        await get_one_call_weather(url="https://test.com", how="city", city_zip="test")

    out, _ = capfd.readouterr()
    assert "Unable" in out


async def test_get_one_callcurrent_weather_https_error(monkeypatch):
    async def mock_get_response(*args, **kwargs):
        return Response(500, request=Request("get", url="https://test.com"))

    monkeypatch.setattr(AsyncClient, "get", mock_get_response)

    with pytest.raises(HTTPStatusError):
        await get_one_call_weather(url="https://test.com", how="city", city_zip="test")


async def test_get_one_call_weather_validation_error(capfd, monkeypatch):
    async def mock_get_response(*args, **kwargs):
        return Response(200, request=Request("get", url="https://test.com"), json={"bad": None})

    monkeypatch.setattr(AsyncClient, "get", mock_get_response)

    with pytest.raises(SystemExit):
        await get_one_call_weather(url="https://test.com", how="city", city_zip="test")

    out, _ = capfd.readouterr()
    assert "Unable" in out
