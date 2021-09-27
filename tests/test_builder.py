import pytest

from weather_command import _builder
from weather_command._config import BASE_URL


@pytest.mark.parametrize("units", ["metric", "imperial"])
@pytest.mark.parametrize("am_pm", [False, True])
def test_current_weather_all(mock_current_weather, units, am_pm):
    table = _builder._current_weather_all(mock_current_weather, units, am_pm)
    assert len(table.columns) == 12
    assert table.row_count == 1


@pytest.mark.parametrize("units", ["metric", "imperial"])
def test_current_weather_temp(mock_current_weather, units):
    table = _builder._current_weather_temp(mock_current_weather, units)
    assert len(table.columns) == 2
    assert table.row_count == 1


@pytest.mark.parametrize("how, city_zip", [("city", "Greensboro"), ("zip", "27405")])
@pytest.mark.parametrize("units", ["metric", "imperial"])
@pytest.mark.parametrize("state_code", ["NC", None])
@pytest.mark.parametrize("country_code", ["US", None])
def test_build_url(how, city_zip, units, state_code, country_code):
    got = _builder._build_url(
        how, city_zip=city_zip, units=units, state_code=state_code, country_code=country_code
    )

    assert got.startswith(BASE_URL)

    if how == "city":
        assert f"weather?q={city_zip}" in got
    else:
        assert f"weather?zip={city_zip}" in got

    assert f"&units={units}" in got

    if state_code:
        assert f"&state_code={state_code}" in got
    else:
        assert f"&state_code={state_code}" not in got

    if country_code:
        assert f"&country_code={country_code}" in got
    else:
        assert f"&country_code={country_code}" not in got


@pytest.mark.parametrize("units, expected", [("metric", "mm"), ("imperial", "in")])
def test_precip_units(units, expected):
    assert _builder._precip_units(units) == expected


def test_precip_units_error():
    with pytest.raises(ValueError):
        _builder._precip_units("bad")


@pytest.mark.parametrize("units, expected", [("metric", "kph"), ("imperial", "mph")])
def test_speed_units(units, expected):
    assert _builder._speed_units(units) == expected


def test_speed_units_error():
    with pytest.raises(ValueError):
        _builder._speed_units("bad")


@pytest.mark.parametrize("units, expected", [("metric", "C"), ("imperial", "F")])
def test_temp_units(units, expected):
    assert _builder._temp_units(units) == expected


def test_temp_units_error():
    with pytest.raises(ValueError):
        _builder._speed_units("bad")
