import pytest
from rich._emoji_codes import EMOJI

from weather_command._weather import WeatherIcons


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
