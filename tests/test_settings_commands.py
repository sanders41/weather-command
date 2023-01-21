import shutil

import pytest
import yaml

from weather_command._config import load_settings
from weather_command.settings_commands import app


@pytest.mark.parametrize("units, time_format", [("imperial", "am/pm"), ("metric", "24 hour")])
def test_all(units, time_format, test_runner, mock_config_dir):
    args = [
        "all",
        "--api-key",
        "test",
        "--temp-only",
        "--time-format",
        time_format,
        "--units",
        units,
    ]
    result = test_runner.invoke(app, args, catch_exceptions=False)
    out = result.stdout

    assert "successfully saved" in out

    settings = load_settings(mock_config_dir)
    assert settings.api_key_file == "test"
    assert settings.temp_only is True
    if time_format == "am/pm":
        assert settings.am_pm is True
    else:
        assert settings.am_pm is False
    if units == "imperial":
        assert settings.imperial is True
    else:
        assert settings.imperial is False


def test_api_key(test_runner, mock_config_dir):
    result = test_runner.invoke(app, ["api-key"], input="test\n", catch_exceptions=False)
    out = result.stdout

    assert "successfully saved" in out

    settings = load_settings(mock_config_dir)

    assert settings.api_key_file == "test"


def test_delete(test_runner, mock_config_dir_with_file):
    result = test_runner.invoke(app, ["delete"], catch_exceptions=False)
    out = result.stdout

    assert "successfully deleted" in out

    file_check = mock_config_dir_with_file / "weather_command.yaml"

    assert file_check.exists() is False


@pytest.mark.parametrize(
    "settings",
    [
        {
            "settings": {
                "api_key": "file",
                "units": "imperial",
                "time_format": "am/pm",
                "temp_only": True,
            }
        },
        {
            "settings": {
                "api_key": "file",
                "units": "metric",
                "time_format": "24 hour",
                "temp_only": False,
            }
        },
    ],
)
def test_saved_settings(settings, test_runner, mock_config_dir):
    with open(mock_config_dir / "weather_command.yaml", "w") as f:
        yaml.safe_dump(settings, f)

    result = test_runner.invoke(app, ["saved-settings"], catch_exceptions=False)
    out = result.stdout

    assert "api_key = MASKED FOR PRIVACY" in out
    assert f"units = {settings['settings']['units']}" in out
    assert f"time_format = {settings['settings']['time_format']}" in out
    assert f"temp_only = {str(settings['settings']['temp_only']).lower()}" in out


def test_saved_settings_invalid_settings(settings, test_runner, mock_config_dir):
    settings = {
        "api_key": "file",
        "units": "metric",
        "time_format": "24 hour",
        "temp_only": False,
    }
    with open(mock_config_dir / "weather_command.yaml", "w") as f:
        yaml.safe_dump(settings, f)

    result = test_runner.invoke(app, ["saved-settings"], catch_exceptions=False)
    out = result.stdout

    assert "Invalid" in out


@pytest.mark.parametrize("temp_only, expected", [("y", True), ("n", False)])
def test_temp_only(temp_only, expected, test_runner, mock_config_dir):
    result = test_runner.invoke(app, ["temp-only"], input=f"{temp_only}\n", catch_exceptions=False)
    out = result.stdout

    assert "successfully saved" in out

    settings = load_settings(mock_config_dir)

    assert settings.temp_only is expected


@pytest.mark.parametrize("time_format, expected", [("am/pm", True), ("24 hour", False)])
def test_time_format(time_format, expected, test_runner, mock_config_dir):
    result = test_runner.invoke(
        app, ["time-format"], input=f"{time_format}\n", catch_exceptions=False
    )
    out = result.stdout

    assert "successfully saved" in out

    settings = load_settings(mock_config_dir)

    assert settings.am_pm is expected


@pytest.mark.parametrize("units, expected", [("imperial", True), ("metric", False)])
def test_units(units, expected, test_runner, mock_config_dir):
    result = test_runner.invoke(app, ["units"], input=f"{units}\n", catch_exceptions=False)
    out = result.stdout

    assert "successfully saved" in out

    settings = load_settings(mock_config_dir)

    assert settings.imperial is expected
