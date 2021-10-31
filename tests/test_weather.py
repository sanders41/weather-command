from unittest.mock import patch

import pytest
from httpx import HTTPStatusError, Request, Response
from rich._emoji_codes import EMOJI

from weather_command._weather import WeatherIcons, get_current_weather, get_one_call_current_weather


@pytest.mark.parametrize(
    "condition, expected",
    [("Sun", ":sun:"), ("broken clouds", ":sun_behind_cloud:"), ("none", None)],
)
def test_get_icon(condition, expected):
    icon = WeatherIcons.get_icon(condition)
    assert icon == expected


@pytest.mark.parametrize("icon", [x.value for x in WeatherIcons])
def test_icons(icon):
    assert icon.replace(":", "") in list(EMOJI.keys())


def test_current_weather_http_error_404(capfd):
    with pytest.raises(SystemExit):
        with patch(
            "httpx.get",
            return_value=Response(404, request=Request("get", url="https://test.com")),
        ):
            get_current_weather(url="https://test.com")

    out, _ = capfd.readouterr()
    assert "Unable" in out


def test_get_current_weather_https_error():
    with pytest.raises(HTTPStatusError):
        with patch(
            "httpx.get",
            return_value=Response(500, request=Request("get", url="https://test.com")),
        ):
            get_current_weather(url="https://test.com")


def test_get_current_weather_validation_error(capfd):
    data = {"bad": None}
    with pytest.raises(SystemExit):
        with patch(
            "httpx.get",
            return_value=Response(200, request=Request("get", url="https://test.com"), json=data),
        ):
            get_current_weather(url="https://test.com")

    out, _ = capfd.readouterr()
    assert "Unable" in out


def test_one_call_current_weather_http_error_404(capfd):
    with pytest.raises(SystemExit):
        with patch(
            "httpx.get",
            return_value=Response(404, request=Request("get", url="https://test.com")),
        ):
            get_one_call_current_weather(url="https://test.com")

    out, _ = capfd.readouterr()
    assert "Unable" in out


def test_get_one_callcurrent_weather_https_error():
    with pytest.raises(HTTPStatusError):
        with patch(
            "httpx.get",
            return_value=Response(500, request=Request("get", url="https://test.com")),
        ):
            get_one_call_current_weather(url="https://test.com")


def test_get_one_call_current_weather_validation_error(capfd):
    data = {"bad": None}
    with pytest.raises(SystemExit):
        with patch(
            "httpx.get",
            return_value=Response(200, request=Request("get", url="https://test.com"), json=data),
        ):
            get_one_call_current_weather(url="https://test.com")

    out, _ = capfd.readouterr()
    assert "Unable" in out
