from __future__ import annotations

import os
import sys
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console
from rich.theme import Theme

from weather_command.errors import MissingApiKey

WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
LOCATION_BASE_URL = "https://nominatim.openstreetmap.org/search?format=json&limit=1"

custom_style = Theme({"error": "red", "date": "green"})
console = Console(theme=custom_style)


@lru_cache(maxsize=16)
def append_api_key(url: str) -> str:
    settings = load_settings()
    api_key = None
    if settings.api_key_env and settings.api_key_file:
        console.print(
            "NOTE: API key present in both environment vairables and settings file, using environment vairable\n\n"
        )
        api_key = settings.api_key_env
    elif settings.api_key_env:
        api_key = settings.api_key_env
    elif settings.api_key_file:
        api_key = settings.api_key_file

    return f"{url}&appid={api_key}"


class TimeFormat(str, Enum):
    AMPM = "am/pm"
    TWENTY_FOUR_HOUR = "24 hour"


class Units(str, Enum):
    IMPERIAL = "imperial"
    METRIC = "metric"


def _get_default_directory() -> Path:
    xdg_config = os.getenv("XDG_CONFIG_HOME")
    settings_path = (
        Path(xdg_config) / "weather_command"
        if xdg_config
        else Path.home() / ".config" / "weather_command"
    )
    return settings_path.resolve()


class Settings:
    get_default_directory = staticmethod(_get_default_directory)

    def __init__(
        self,
        settings_dir: Path | None = None,
        api_key_env: str | None = os.getenv("OPEN_WEATHER_API_KEY"),
        api_key_file: str | None = None,
        imperial: bool | None = None,
        temp_only: bool | None = None,
        am_pm: bool | None = None,
    ) -> None:
        self.settings_dir = settings_dir or Settings.get_default_directory()
        self._settings_file = self.settings_dir / "weather_command.yaml"
        self.api_key_env = api_key_env
        self.api_key_file = api_key_file
        self.imperial = imperial
        self.temp_only = temp_only
        self.am_pm = am_pm

    @property
    def display_values(self) -> str:
        values = ""
        if self.api_key_file:
            values = "api_key = [green]MASKED FOR PRIVACY[/green]\n"
        if self.imperial is not None:
            if self.imperial:
                values = f"{values}units = [green]imperial[/green]\n"
            else:
                values = f"{values}units = [green]metric[/green]\n"
        if self.temp_only is not None:
            values = f"{values}temp_only = [green]{str(self.temp_only).lower()}[/green]\n"
        if self.am_pm is not None:
            if self.am_pm:
                values = f"{values}time_format = [green]am/pm[/green]\n"
            else:
                values = f"{values}time_format = [green]24 hour[/green]\n"

        return values or "No settings saved"

    def delete(self) -> None:
        if self._settings_file.exists():
            self._settings_file.unlink()

    def load(self) -> None:
        self.api_key_env = os.getenv("OPEN_WEATHER_API_KEY")

        settings = None
        if self._settings_file.exists():
            with open(self._settings_file) as f:
                settings = yaml.safe_load(f)

            if not settings.get("settings"):
                console.print("[red]Invalid settings file[/red]")
                sys.exit(1)

        if settings:
            self.api_key_file = settings["settings"].get("api_key")
            self.imperial = (
                settings["settings"].get("units") == Units.IMPERIAL.value
                if settings["settings"].get("units")
                else None
            )
            self.temp_only = settings["settings"].get("temp_only")
            self.am_pm = (
                settings["settings"].get("time_format") == TimeFormat.AMPM.value
                if settings["settings"].get("time_format")
                else None
            )

        if not self.api_key_env and not self.api_key_file:
            raise MissingApiKey(
                "An environment variable named OPEN_WEATHER_API_KEY or weather_command.yaml file containing the API key is required"
            )

    def save(self) -> None:
        settings: dict[str, Any] = {}
        if not self.settings_dir.exists():
            self.settings_dir.mkdir(parents=True)

        if self.api_key_file:
            settings["api_key"] = self.api_key_file

        if self.imperial is not None:
            settings["units"] = Units.IMPERIAL.value if self.imperial else Units.METRIC.value

        if self.temp_only is not None:
            settings["temp_only"] = self.temp_only

        if self.am_pm is not None:
            settings["time_format"] = (
                TimeFormat.AMPM.value if self.am_pm else TimeFormat.TWENTY_FOUR_HOUR.value
            )

        if settings:
            with open(self._settings_file, "w") as f:
                yaml.safe_dump({"settings": settings}, f)


@lru_cache(maxsize=1)
def load_settings(settings_dir: Path | None = None) -> Settings:
    settings = Settings(settings_dir)
    settings.load()
    return settings
