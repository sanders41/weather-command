import pytest

from weather_command._weather import WeatherIcons


@pytest.mark.parametrize(
    "condition, expected",
    [("Sun", ":sun:"), ("broken clouds", ":sun_behind_cloud:"), ("none", None)],
)
def test_get_icon(condition, expected):
    icon = WeatherIcons.get_icon(condition)
    assert icon == expected
