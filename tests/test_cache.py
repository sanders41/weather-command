import json
import os
from datetime import date, datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from weather_command._cache import DateTimeEncoder, _get_default_directory


def test_encoder(tmp_path):
    data = {
        "string": "string",
        "float": 1.1,
        "integer": 1,
        "date": date(2021, 12, 21),
        "date_time": datetime(2021, 12, 21, 22, 56, 1, 141153),
    }

    cache_file = tmp_path / "test.json"

    with open(cache_file, "w") as f:
        json.dump(data, f, cls=DateTimeEncoder)

    with open(cache_file, "r") as f:
        result = json.load(f)

    data["date"] = str(data["date"])
    data["date_time"] = str(data["date_time"]).replace(" ", "T")

    assert result == data


def test_get_default_directory_defaults_to_home():
    directory = _get_default_directory()
    expected = Path(os.path.realpath(os.path.expanduser("~/.cache/weather-command")))
    assert directory == expected


def test_adheres_to_xdg_specification():
    with patch.dict(os.environ, {"XDG_CACHE_HOME": "/tmp/fakehome"}):
        directory = _get_default_directory()

    expected = Path(os.path.realpath("/tmp/fakehome/weather-command"))
    assert directory == expected


@pytest.mark.parametrize(
    "use_location, use_current_weather, use_one_call_weather",
    (
        (True, False, False),
        (False, True, False),
        (False, False, True),
        (True, True, True),
    ),
)
def test_add_no_cache_hit(
    mock_location,
    mock_current_weather,
    mock_one_call_weather,
    use_location,
    use_current_weather,
    use_one_call_weather,
    cache_with_file,
):
    if use_location:
        location = mock_location
    else:
        location = None

    if use_current_weather:
        current_weather = mock_current_weather
    else:
        current_weather = None

    if use_one_call_weather:
        one_call_weather = mock_one_call_weather
    else:
        one_call_weather = None

    city_zip = "27405"

    cache_with_file.add(
        city_zip=city_zip,
        location=location,
        current_weather=current_weather,
        one_call_weather=one_call_weather,
    )

    with open(cache_with_file._cache_file, "r") as f:
        cache_values = json.load(f)

    assert cache_values is not None
    if use_location:
        assert cache_values[city_zip]["location"] is not None
    else:
        assert cache_values[city_zip]["location"] is None

    if use_current_weather:
        assert cache_values[city_zip]["currentWeather"] is not None
    else:
        assert cache_values[city_zip]["currentWeather"] is None

    if use_one_call_weather:
        assert cache_values[city_zip]["oneCallWeather"] is not None
    else:
        assert cache_values[city_zip]["oneCallWeather"] is None


def test_add_eject(
    mock_location,
    mock_current_weather,
    mock_one_call_weather,
    cache_with_file,
):
    city_zip = "27405"

    cache_with_file.add(
        city_zip=city_zip,
        location=mock_location,
        current_weather=mock_current_weather,
        one_call_weather=mock_one_call_weather,
        cache_size=1,
    )

    with open(cache_with_file._cache_file, "r") as f:
        cache_values = json.load(f)

    assert cache_values is not None
    keys = cache_values.keys()
    assert city_zip in keys
    assert len(keys) == 1


@pytest.mark.parametrize(
    "use_location, use_current_weather, use_one_call_weather",
    (
        (True, False, False),
        (False, True, False),
        (False, False, True),
        (True, True, True),
    ),
)
@patch("weather_command._cache.datetime")
def test_add_cache_hit(
    mock_dt,
    mock_location,
    mock_current_weather,
    mock_one_call_weather,
    use_location,
    use_current_weather,
    use_one_call_weather,
    cache_with_file,
):
    mock_dt.utcnow = Mock(return_value=datetime(2021, 12, 22, 1, 36, 38))
    if use_location:
        location = mock_location
    else:
        location = None

    if use_current_weather:
        current_weather = mock_current_weather
    else:
        current_weather = None

    if use_one_call_weather:
        one_call_weather = mock_one_call_weather
    else:
        one_call_weather = None

    city_zip = "27455"

    cache_with_file.add(
        city_zip=city_zip,
        location=location,
        current_weather=current_weather,
        one_call_weather=one_call_weather,
    )

    with open(cache_with_file._cache_file, "r") as f:
        cache_values = json.load(f)

    assert cache_values is not None
    assert cache_values[city_zip]["location"] is not None
    assert cache_values[city_zip]["currentWeather"] is not None
    assert cache_values[city_zip]["oneCallWeather"] is not None


def test_clear(cache):
    data = {"test": "test"}

    with open(cache._cache_file, "w") as f:
        json.dump(data, f)

    assert cache._cache_file.exists()

    cache.clear()

    assert not cache._cache_file.exists()


@patch("weather_command._cache.datetime")
def test_get(mock_dt, cache_with_file):
    mock_dt.utcnow = Mock(return_value=datetime(2021, 12, 22, 1, 36, 38))
    cache_values = cache_with_file.get("27455")

    assert cache_values is not None
    assert cache_values.current_weather is not None
    assert cache_values.one_call_weather is not None


def test_get_expired(cache_with_file):
    cache_values = cache_with_file.get("27455")

    assert cache_values is not None
    assert cache_values.current_weather is None
    assert cache_values.one_call_weather is None


def test_load(cache_with_file):
    assert cache_with_file._cache is not None


def test_load_none(cache):
    assert cache._cache is None
