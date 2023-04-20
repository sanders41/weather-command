from __future__ import annotations

import json
import os
from datetime import date, datetime
from json import JSONEncoder
from pathlib import Path
from typing import Any, Optional

from camel_converter.pydantic_base import CamelBase

from weather_command.models.location import Location
from weather_command.models.weather import CurrentWeather, OneCallWeather


class CacheDuration(CamelBase):
    cache_duration_minutes: int = 15
    date_time_saved: datetime


class CurrentWeatherCache(CacheDuration):
    current_weather: CurrentWeather


class OneCallWeatherCache(CacheDuration):
    one_call_weather: OneCallWeather


class CacheItem(CamelBase):
    location: Optional[Location] = None
    current_weather: Optional[CurrentWeatherCache] = None
    one_call_weather: Optional[OneCallWeatherCache] = None


class DateTimeEncoder(JSONEncoder):
    """Subclass the default encoder to be able to encode dates."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()


def _get_default_directory() -> Path:
    xdg_cache = os.getenv("XDG_CACHE_HOME")
    settings_path = (
        Path(xdg_cache) / "weather-command"
        if xdg_cache
        else Path.home() / ".cache" / "weather-command"
    )
    return settings_path.resolve()


class Cache:
    get_default_directory = staticmethod(_get_default_directory)

    def __init__(self, cache_dir: Path | None = None) -> None:
        self.cache_dir = cache_dir or Cache.get_default_directory()
        self._cache_file = self.cache_dir / "cache.json"
        if not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True)

        self._cache: dict[str, CacheItem] | None = self._load()

    def add(
        self,
        *,
        cache_key: str,
        location: Location | None = None,
        current_weather: CurrentWeather | None = None,
        one_call_weather: OneCallWeather | None = None,
        cache_size: int = 5,
    ) -> None:
        def save_cache() -> None:
            cache: dict[str, Any] = {}
            location_cache = location.dict() if location else None
            current_weather_cache = (
                CurrentWeatherCache(
                    date_time_saved=datetime.utcnow(), current_weather=current_weather
                ).dict()
                if current_weather
                else None
            )
            one_call_weather_cache = (
                OneCallWeatherCache(
                    date_time_saved=datetime.utcnow(), one_call_weather=one_call_weather
                ).dict()
                if one_call_weather
                else None
            )

            cache_hit = self.get(cache_key)

            if cache_hit:
                cache[cache_key.lower()] = {
                    "location": cache_hit.location.dict()
                    if cache_hit.location and not location_cache
                    else location_cache,
                    "currentWeather": cache_hit.current_weather.dict()
                    if cache_hit.current_weather and not current_weather_cache
                    else current_weather_cache,
                    "oneCallWeather": cache_hit.one_call_weather.dict()
                    if cache_hit.one_call_weather and not one_call_weather_cache
                    else one_call_weather_cache,
                }
            else:
                cache[cache_key.lower()] = {
                    "location": location_cache,
                    "currentWeather": current_weather_cache,
                    "oneCallWeather": one_call_weather_cache,
                }

            if self._cache:
                for key in self._cache:
                    if key != cache_key:
                        saved_cache = self._cache[key]
                        cache[key] = saved_cache.dict()

            with open(self._cache_file, "w") as f:
                json.dump(cache, f, cls=DateTimeEncoder)

        if not self._cache or len(self._cache.keys()) < cache_size:
            save_cache()
        else:
            last_key = list(self._cache.keys())[-1]
            del self._cache[last_key]
            save_cache()

    def clear(self) -> None:
        if self._cache_file.exists():
            self._cache_file.unlink()

    def get(self, cache_key: str) -> CacheItem | None:
        if not self._cache or not self._cache.get(cache_key):
            return None

        cache = self._cache[cache_key.lower()]
        if cache.current_weather:
            time_diff = datetime.utcnow() - cache.current_weather.date_time_saved
            if (time_diff.total_seconds() / 60) > cache.current_weather.cache_duration_minutes:
                cache.current_weather = None

        if cache.one_call_weather:
            time_diff = datetime.utcnow() - cache.one_call_weather.date_time_saved
            if (time_diff.total_seconds() / 60) > cache.one_call_weather.cache_duration_minutes:
                cache.one_call_weather = None

        return cache

    def _load(self) -> dict[str, CacheItem] | None:
        if not self._cache_file.exists():
            return None

        with open(self._cache_file, "r") as f:
            json_cache = json.load(f)

        return {k: CacheItem(**v) for k, v in json_cache.items()}
