from __future__ import annotations

from datetime import datetime, timedelta

from rich.console import Console
from rich.table import Table

from weather_command._config import BASE_URL, apppend_api_key
from weather_command._weather import WeatherIcons, get_current_weather
from weather_command.models.weather import CurrentWeather


def show_current(
    how: str,
    *,
    city_zip: str,
    state_code: str | None = None,
    country_code: str | None = None,
    units: str = "metric",
    am_pm: bool = False,
    temp_only: bool = False,
    terminal_width: int | None = None,
) -> None:
    url = _build_url(how, city_zip, units, state_code, country_code)

    console = Console()
    if terminal_width:
        console.width = terminal_width

    with console.status("Getting weather..."):
        current_weather = get_current_weather(url)

    if not temp_only:
        console.print(_current_weather_all(current_weather, units, am_pm))
    else:
        console.print(_current_weather_temp(current_weather, units))


def _build_url(
    how: str, city_zip: str, units: str, state_code: str | None, country_code: str | None
) -> str:
    if how == "city":
        url = f"{BASE_URL}/weather?q={city_zip}&units={units}"
    else:
        url = f"{BASE_URL}/weather?zip={city_zip}&units={units}"

    if state_code:
        url = f"{url}&state_code={state_code}"

    if country_code:
        url = f"{url}&country_code={country_code}"

    return apppend_api_key(url)


def _current_weather_all(current_weather: CurrentWeather, units: str, am_pm: bool) -> Table:
    temp_unit = _temp_units(units)
    speed_unit = _speed_units(units)
    precip_unit = _precip_units(units)
    conditions = current_weather.weather[0].description
    weather_icon = WeatherIcons.get_icon(conditions)
    if weather_icon:
        conditions += f" {weather_icon}"
    if not am_pm:
        sunrise = str(
            (current_weather.sys.sunrise + timedelta(seconds=current_weather.timezone)).time()
        )
        sunset = str(
            (current_weather.sys.sunset + timedelta(seconds=current_weather.timezone)).time()
        )
    else:
        sunrise = datetime.strftime(
            (current_weather.sys.sunrise + timedelta(seconds=current_weather.timezone)), "%I:%M %p"
        )
        sunset = datetime.strftime(
            (current_weather.sys.sunset + timedelta(seconds=current_weather.timezone)), "%I:%M %p"
        )

    table = Table(title=f"Current weather for {current_weather.name}")
    table.add_column(f"Temperature ({temp_unit}) :thermometer:")
    table.add_column(f"Feels Like ({temp_unit}) :thermometer:")
    table.add_column("Humidity")
    table.add_column("Conditions")
    table.add_column(f"Low ({temp_unit}) :thermometer:")
    table.add_column(f"High ({temp_unit}) :thermometer:")
    table.add_column(f"Wind Speed ({speed_unit})")
    table.add_column(f"Wind Gusts ({speed_unit})")
    table.add_column(f"Rain 1 Hour ({precip_unit}) :cloud_with_rain:")
    table.add_column(f"Rain 3 Hour ({precip_unit}) :cloud_with_rain:")
    table.add_column(f"Snow 1 Hour ({precip_unit}) :snowflake:")
    table.add_column(f"Snow 3 Hour ({precip_unit}) :snowflake:")
    table.add_column("Sunrise :sunrise:")
    table.add_column("Sunset :sunset:")
    table.add_row(
        str(round(current_weather.main.temp)),
        str(round(current_weather.main.feels_like)),
        f"{current_weather.main.humidity}%" if current_weather.main.humidity else "0%",
        conditions,
        str(round(current_weather.main.temp_min)),
        str(round(current_weather.main.temp_max)),
        str(round(current_weather.wind.speed))
        if current_weather.wind and current_weather.wind.speed
        else "0",
        str(round(current_weather.wind.gust))
        if current_weather.wind and current_weather.wind.gust
        else "0",
        (str(current_weather.rain.one_hour) if current_weather.rain.one_hour else "0")
        if current_weather.rain
        else "0",
        (str(current_weather.rain.three_hour) if current_weather.rain.three_hour else "0")
        if current_weather.rain
        else "0",
        (str(current_weather.snow.one_hour) if current_weather.snow.one_hour else "0")
        if current_weather.snow
        else "0",
        (str(current_weather.snow.three_hour) if current_weather.snow.three_hour else "0")
        if current_weather.snow
        else "0",
        sunrise,
        sunset,
    )

    return table


def _current_weather_temp(current_weather: CurrentWeather, units: str) -> Table:
    temp_unit = _temp_units(units)

    table = Table(title=f"Current weather for {current_weather.name}")
    table.add_column(f"Temperature ({temp_unit}) :thermometer:")
    table.add_column(f"Feels Like ({temp_unit}) :thermometer:")
    table.add_column(f"Low ({temp_unit}) :thermometer:")
    table.add_column(f"High ({temp_unit}) :thermometer:")
    table.add_row(
        str(round(current_weather.main.temp)),
        str(round(current_weather.main.feels_like)),
        str(round(current_weather.main.temp_min)),
        str(round(current_weather.main.temp_max)),
    )

    return table


def _precip_units(units: str) -> str:
    _validate_units(units)
    return "mm" if units == "metric" else "in"


def _speed_units(units: str) -> str:
    _validate_units(units)
    return "kph" if units == "metric" else "mph"


def _temp_units(units: str) -> str:
    _validate_units(units)
    return "C" if units == "metric" else "F"


def _validate_units(units: str) -> None:
    if units not in ["metric", "imperial"]:
        raise ValueError("Units must either be metric or imperial")
