import os
import shutil
from pathlib import Path
from unittest.mock import patch

from weather_command._config import Settings, _get_default_directory


def test_get_default_directory_defaults_to_home():
    directory = _get_default_directory()
    expected = Path(os.path.realpath(os.path.expanduser("~/.config/weather_command")))
    assert directory == expected


def test_adheres_to_xdg_specification():
    with patch.dict(os.environ, {"XDG_CONFIG_HOME": "/tmp/fakehome"}):
        directory = _get_default_directory()

    expected = Path(os.path.realpath("/tmp/fakehome/weather_command"))
    assert directory == expected


def test_save_creates_dir(mock_config_dir):
    settings = Settings(settings_dir=mock_config_dir, api_key_file="file")
    settings_file = mock_config_dir / settings._settings_file

    shutil.rmtree(mock_config_dir)
    settings.save()

    assert settings_file.exists()
