import httpx
import pytest
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


def test_current_weather_http_error_404(capfd, monkeypatch):
    def mock_get_response(*args, **kwargs):
        return httpx.Response(404, request=httpx.Request("get", url="https://test.com"))

    monkeypatch.setattr(httpx, "get", mock_get_response)

    with pytest.raises(SystemExit):
        get_current_weather(url="https://test.com", how="city", city_zip="test")

    out, _ = capfd.readouterr()
    assert "Unable" in out


def test_get_current_weather_https_error(monkeypatch):
    def mock_get_response(*args, **kwargs):
        return httpx.Response(500, request=httpx.Request("get", url="https://test.com"))

    monkeypatch.setattr(httpx, "get", mock_get_response)

    with pytest.raises(httpx.HTTPStatusError):
        get_current_weather(url="https://test.com", how="city", city_zip="test")


def test_get_current_weather_validation_error(capfd, monkeypatch):
    def mock_get_response(*args, **kwargs):
        return httpx.Response(
            200, request=httpx.Request("get", url="https://test.com"), json={"bad": None}
        )

    monkeypatch.setattr(httpx, "get", mock_get_response)

    with pytest.raises(SystemExit):
        get_current_weather(url="https://test.com", how="city", city_zip="test")

    out, _ = capfd.readouterr()
    assert "Unable" in out


def test_one_call_current_weather_http_error_404(capfd, monkeypatch):
    def mock_get_response(*args, **kwargs):
        return httpx.Response(404, request=httpx.Request("get", url="https://test.com"))

    monkeypatch.setattr(httpx, "get", mock_get_response)

    with pytest.raises(SystemExit):
        get_one_call_weather(url="https://test.com", how="city", city_zip="test")

    out, _ = capfd.readouterr()
    assert "Unable" in out


def test_get_one_callcurrent_weather_https_error(monkeypatch):
    def mock_get_response(*args, **kwargs):
        return httpx.Response(500, request=httpx.Request("get", url="https://test.com"))

    monkeypatch.setattr(httpx, "get", mock_get_response)

    with pytest.raises(httpx.HTTPStatusError):
        get_one_call_weather(url="https://test.com", how="city", city_zip="test")


def test_get_one_call_weather_validation_error(capfd, monkeypatch):
    def mock_get_response(*args, **kwargs):
        return httpx.Response(
            200, request=httpx.Request("get", url="https://test.com"), json={"bad": None}
        )

    monkeypatch.setattr(httpx, "get", mock_get_response)

    with pytest.raises(SystemExit):
        get_one_call_weather(url="https://test.com", how="city", city_zip="test")

    out, _ = capfd.readouterr()
    assert "Unable" in out
