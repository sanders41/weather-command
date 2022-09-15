from __future__ import annotations

from datetime import datetime, timedelta
from functools import lru_cache

from rich.style import Style
from rich.table import Table

from weather_command._cache import Cache
from weather_command._config import WEATHER_BASE_URL, append_api_key, console
from weather_command._location import get_location_details
from weather_command._weather import get_current_weather, get_icon, get_one_call_weather
from weather_command.models.location import Location
from weather_command.models.weather import CurrentWeather, OneCallWeather

HEADER_ROW_STYLE = Style(color="sky_blue2", bold=True)


async def show_current(
    how: str,
    city_zip: str,
    *,
    state_code: str | None = None,
    country_code: str | None = None,
    units: str = "metric",
    am_pm: bool = False,
    temp_only: bool = False,
    terminal_width: int | None = None,
) -> None:
    def print_weather(current_weather: CurrentWeather, location: Location) -> None:
        if not temp_only:
            console.print(current_weather_all(current_weather, units, am_pm, location))
        else:
            console.print(_current_weather_temp(current_weather, units, location))

    if terminal_width:
        console.width = terminal_width

    with console.status("Getting weather..."):
        current_weather: CurrentWeather

        if how == "zip":
            cache = Cache()
            cache_hit = cache.get(city_zip)
            if cache_hit:
                if cache_hit.location:
                    location = cache_hit.location
                else:
                    location = await get_location_details(
                        how=how, city_zip=city_zip, state=state_code, country=country_code
                    )
                if cache_hit.current_weather:
                    current_weather = cache_hit.current_weather.current_weather
                    print_weather(cache_hit.current_weather.current_weather, location)
                    return None
                else:
                    url = build_url(
                        forecast_type="current",
                        units=units,
                        lon=location.lon,
                        lat=location.lat,
                    )
                    current_weather = await get_current_weather(url, how, city_zip)
                    print_weather(current_weather, location)
                    return None

        location = await get_location_details(
            how=how, city_zip=city_zip, state=state_code, country=country_code
        )

        url = build_url(
            forecast_type="current",
            units=units,
            lon=location.lon,
            lat=location.lat,
        )
        current_weather = await get_current_weather(url, how, city_zip)
        print_weather(current_weather, location)


async def show_daily(
    how: str,
    city_zip: str,
    *,
    state_code: str | None = None,
    country_code: str | None = None,
    units: str = "metric",
    am_pm: bool = False,
    temp_only: bool = False,
    terminal_width: int | None = None,
) -> None:
    def print_weather(weather: OneCallWeather, location: Location) -> None:
        if not temp_only:
            console.print(daily_all(weather, units, am_pm, location))
        else:
            console.print(_daily_temp_only(weather, units, am_pm, location))

    if terminal_width:
        console.width = terminal_width

    with console.status("Getting weather..."):
        weather: OneCallWeather

        if how == "zip":
            cache = Cache()
            cache_hit = cache.get(city_zip)
            if cache_hit:
                if cache_hit.location:
                    location = cache_hit.location
                else:
                    location = await get_location_details(
                        how=how, city_zip=city_zip, state=state_code, country=country_code
                    )
                if cache_hit.one_call_weather:
                    print_weather(cache_hit.one_call_weather.one_call_weather, location)
                    return None
                else:
                    url = build_url(
                        forecast_type="daily", units=units, lon=location.lon, lat=location.lat
                    )
                    weather = await get_one_call_weather(url, how, city_zip)
                    print_weather(weather, location)
                    return None

        location = await get_location_details(
            how=how, city_zip=city_zip, state=state_code, country=country_code
        )

        url = build_url(forecast_type="daily", units=units, lon=location.lon, lat=location.lat)
        weather = await get_one_call_weather(url, how, city_zip)
        print_weather(weather, location)


async def show_hourly(
    how: str,
    city_zip: str,
    *,
    state_code: str | None = None,
    country_code: str | None = None,
    units: str = "metric",
    am_pm: bool = False,
    temp_only: bool = False,
    terminal_width: int | None = None,
) -> None:
    def print_weather(weather: OneCallWeather, location: Location) -> None:
        if not temp_only:
            console.print(hourly_all(weather, units, am_pm, location))
        else:
            console.print(_hourly_temp_only(weather, units, am_pm, location))

    if terminal_width:
        console.width = terminal_width

    with console.status("Getting weather..."):
        weather: OneCallWeather

        if how == "zip":
            cache = Cache()
            cache_hit = cache.get(city_zip)
            if cache_hit:
                if cache_hit.location:
                    location = cache_hit.location
                else:
                    location = await get_location_details(
                        how=how, city_zip=city_zip, state=state_code, country=country_code
                    )
                if cache_hit.one_call_weather:
                    print_weather(cache_hit.one_call_weather.one_call_weather, location)
                    return None
                else:
                    url = build_url(
                        forecast_type="hourly", units=units, lon=location.lon, lat=location.lat
                    )
                    weather = await get_one_call_weather(url, how, city_zip)
                    print_weather(weather, location)
                    return None

        location = await get_location_details(
            how=how, city_zip=city_zip, state=state_code, country=country_code
        )

        url = build_url(forecast_type="hourly", units=units, lon=location.lon, lat=location.lat)
        weather = await get_one_call_weather(url, how, city_zip)
        print_weather(weather, location)


def build_url(
    forecast_type: str,
    units: str,
    lon: float | None = None,
    lat: float | None = None,
) -> str:
    if forecast_type == "current":
        url = f"{WEATHER_BASE_URL}/weather?lat={lat}&lon={lon}&units={units}"
    else:
        url = f"{WEATHER_BASE_URL}/onecall?lat={lat}&lon={lon}&units={units}"

    return append_api_key(url)


def current_weather_all(
    current_weather: CurrentWeather,
    units: str,
    am_pm: bool,
    location: Location,
    show_title: bool = True,
) -> Table:
    precip_unit, _, speed_units, temp_units = _get_units(units)
    conditions = current_weather.weather[0].description
    weather_icon = get_icon(conditions)
    if weather_icon:
        conditions = f"{conditions} {weather_icon}"
    sunrise, sunset = _format_sunrise_sunset(
        am_pm, current_weather.sys.sunrise, current_weather.sys.sunset, current_weather.timezone
    )

    table = (
        Table(
            title=f"Current weather for {location.display_name}",
            header_style=HEADER_ROW_STYLE,
            expand=True,
        )
        if show_title
        else Table(header_style=HEADER_ROW_STYLE, show_lines=True, expand=True)
    )
    table.add_column(f"Temperature ({temp_units}) :thermometer:")
    table.add_column(f"Feels Like ({temp_units}) :thermometer:")
    table.add_column("Humidity")
    table.add_column("Conditions")
    table.add_column(f"Wind Speed ({speed_units})")
    table.add_column(f"Wind Gusts ({speed_units})")
    table.add_column(f"Rain 1 Hour ({precip_unit}) :cloud_with_rain:")
    table.add_column(f"Rain 3 Hour ({precip_unit}) :cloud_with_rain:")
    table.add_column(f"Snow 1 Hour ({precip_unit}) :snowflake:")
    table.add_column(f"Snow 3 Hour ({precip_unit}) :snowflake:")
    table.add_column("Sunrise :sunrise:")
    table.add_column("Sunset :sunset:")

    if current_weather.rain:
        rain_one_hour = _format_precip(current_weather.rain.one_hour, units)
        rain_three_hour = _format_precip(current_weather.rain.three_hour, units)
    else:
        rain_one_hour = "0.00"
        rain_three_hour = "0.00"

    if current_weather.snow:
        snow_one_hour = _format_precip(current_weather.snow.one_hour, units)
        snow_three_hour = _format_precip(current_weather.snow.three_hour, units)
    else:
        snow_one_hour = "0.00"
        snow_three_hour = "0.00"

    if current_weather.wind:
        wind = _format_wind(current_weather.wind.speed, units)
        gusts = _format_wind(current_weather.wind.gust, units)
    else:
        wind = "0"
        gusts = "0"

    table.add_row(
        str(_round_to_int(current_weather.main.temp)),
        str(_round_to_int(current_weather.main.feels_like)),
        f"{current_weather.main.humidity}%" if current_weather.main.humidity else "0%",
        conditions,
        wind,
        gusts,
        rain_one_hour,
        rain_three_hour,
        snow_one_hour,
        snow_three_hour,
        sunrise,
        sunset,
    )

    return table


def _current_weather_temp(current_weather: CurrentWeather, units: str, location: Location) -> Table:
    _, _, _, temp_units = _get_units(units)

    table = Table(
        title=f"Current weather for {location.display_name}", header_style=HEADER_ROW_STYLE
    )
    table.add_column(f"Temperature ({temp_units}) :thermometer:")
    table.add_column(f"Feels Like ({temp_units}) :thermometer:")
    table.add_row(
        str(_round_to_int(current_weather.main.temp)),
        str(_round_to_int(current_weather.main.feels_like)),
    )

    return table


def daily_all(
    weather: OneCallWeather, units: str, am_pm: bool, location: Location, show_title: bool = True
) -> Table:
    _, pressure_units, speed_units, temp_units = _get_units(units)
    table = (
        Table(
            title=f"Hourly weather for {location.display_name}",
            header_style=HEADER_ROW_STYLE,
            show_lines=True,
            expand=True,
        )
        if show_title
        else Table(header_style=HEADER_ROW_STYLE, show_lines=True, expand=True)
    )
    table.add_column("Date/Day :date:")
    table.add_column(f"Low ({temp_units}) :thermometer:")
    table.add_column(f"High ({temp_units}) :thermometer:")
    table.add_column("Humidity")
    table.add_column(f"Dew Point ({temp_units})")
    table.add_column(f"Pressure {pressure_units}")
    table.add_column("Conditions")
    table.add_column("UVI")
    table.add_column("Clouds")
    table.add_column("Precipitation Chance")
    table.add_column(f"Wind ({speed_units})")
    table.add_column(f"Wind Gusts {speed_units}")
    table.add_column("Sunrise :sunrise:")
    table.add_column("Sunset :sunset:")

    for daily in weather.daily:
        dt = _format_date_time(am_pm, daily.dt, weather.timezone_offset, "daily")
        sunrise, sunset = _format_sunrise_sunset(
            am_pm, daily.sunrise, daily.sunset, weather.timezone_offset
        )
        conditions = daily.weather[0].description
        weather_icon = get_icon(conditions)
        if weather_icon:
            conditions = f"{conditions} {weather_icon}"

        wind = _format_wind(daily.wind_speed, units)
        gusts = _format_wind(daily.wind_gust, units)
        pressure = _format_pressure(daily.pressure, units)

        table.add_row(
            dt,
            str(_round_to_int(daily.temp.min)),
            str(_round_to_int(daily.temp.max)),
            f"{daily.humidity}%",
            str(_round_to_int(daily.dew_point)),
            pressure,
            conditions,
            str(daily.uvi),
            f"{daily.clouds}%",
            f"{_round_to_int(daily.pop * 100)}%",
            wind,
            gusts,
            sunrise,
            sunset,
        )

    return table


def _daily_temp_only(weather: OneCallWeather, units: str, am_pm: bool, location: Location) -> Table:
    _, _, _, temp_units = _get_units(units)
    table = Table(
        title=f"Hourly weather for {location.display_name}",
        header_style=HEADER_ROW_STYLE,
        show_lines=True,
    )
    table.add_column("Date/Day :date:")
    table.add_column(f"Low ({temp_units}) :thermometer:")
    table.add_column(f"High ({temp_units}) :thermometer:")

    for daily in weather.daily:
        dt = _format_date_time(am_pm, daily.dt, weather.timezone_offset, "daily")

        table.add_row(
            dt,
            str(_round_to_int(daily.temp.min)),
            str(_round_to_int(daily.temp.max)),
        )

    return table


@lru_cache(maxsize=256)
def _format_date_time(
    am_pm: bool, dt: datetime, timezone: int, forecast_type: str | None = None
) -> str:
    if forecast_type == "daily":
        return f"[date]{datetime.strftime(dt + timedelta(seconds=timezone), '%d-%b-%Y %A')}[/]"

    if not am_pm:
        return f"[date]{datetime.strftime(dt + timedelta(seconds=timezone), '%d-%b-%Y %H:%M')}[/]"
    else:
        return (
            f"[date]{datetime.strftime(dt + timedelta(seconds=timezone), '%d-%b-%Y %I:%M %p')}[/]"
        )


@lru_cache(maxsize=256)
def _format_precip(precip_amount: float | None, units: str) -> str:
    if not precip_amount:
        return "0.00"

    return str(_mm_to_in(precip_amount)) if units == "imperial" else str(precip_amount)


@lru_cache(maxsize=256)
def _format_pressure(pressure: int | None, units: str) -> str:
    if not pressure:
        return "0"

    return str(_hpa_to_in(pressure)) if units == "imperial" else str(pressure)


@lru_cache(maxsize=256)
def _format_wind(speed: float | None, units: str) -> str:
    if not speed:
        return "0"

    return (
        str(_round_to_int(_kph_to_mph(speed))) if units == "imperial" else str(_round_to_int(speed))
    )


@lru_cache(maxsize=256)
def _format_sunrise_sunset(
    am_pm: bool, sunrise: datetime, sunset: datetime, timezone: int
) -> tuple[str, str]:
    if not am_pm:
        sunrise_format = str((sunrise + timedelta(seconds=timezone)).time())
        sunset_format = str((sunset + timedelta(seconds=timezone)).time())
        return sunrise_format, sunset_format

    sunrise_format = datetime.strftime((sunrise + timedelta(seconds=timezone)), "%I:%M %p")
    sunset_format = datetime.strftime((sunset + timedelta(seconds=timezone)), "%I:%M %p")
    return sunrise_format, sunset_format


@lru_cache(maxsize=2)
def _get_units(units: str) -> tuple[str, str, str, str]:
    _validate_units(units)
    if units == "metric":
        precip_units = "mm"
        pressure_units = "hPa"
        speed_units = "kph"
        temp_units = "C"
        return precip_units, pressure_units, speed_units, temp_units

    precip_units = "in"
    pressure_units = "in"
    speed_units = "mph"
    temp_units = "F"
    return precip_units, pressure_units, speed_units, temp_units


def hourly_all(
    weather: OneCallWeather, units: str, am_pm: bool, location: Location, show_title: bool = True
) -> Table:
    precip_units, pressure_units, speed_units, temp_units = _get_units(units)
    table = (
        Table(
            title=f"Hourly weather for {location.display_name}",
            header_style=HEADER_ROW_STYLE,
            show_lines=True,
        )
        if show_title
        else Table(header_style=HEADER_ROW_STYLE, show_lines=True, expand=True)
    )
    table.add_column("Date/Time :date:")
    table.add_column(f"Temperature ({temp_units}) :thermometer:")
    table.add_column(f"Feels Like ({temp_units}) :thermometer:")
    table.add_column("Humidity")
    table.add_column(f"Dew Point ({temp_units})")
    table.add_column(f"Pressure {pressure_units}")
    table.add_column("Conditions")
    table.add_column("UVI")
    table.add_column("Clouds")
    table.add_column(f"Wind ({speed_units})")
    table.add_column(f"Wind Gusts {speed_units}")
    table.add_column("Precipitation Chance")
    table.add_column(f"Rain ({precip_units}) :cloud_with_rain:")
    table.add_column(f"Snow ({precip_units}) :snowflake:")

    for hourly in weather.hourly:
        dt = _format_date_time(am_pm, hourly.dt, weather.timezone_offset)
        rain = _format_precip(hourly.rain.one_hour, units) if hourly.rain else "0.00"
        snow = _format_precip(hourly.snow.one_hour, units) if hourly.snow else "0.00"
        wind = _format_wind(hourly.wind_speed, units)
        gusts = _format_wind(hourly.wind_gust, units)
        pressure = _format_pressure(hourly.pressure, units)
        conditions = hourly.weather[0].description
        weather_icon = get_icon(conditions)
        if weather_icon:
            conditions = f"{conditions} {weather_icon}"

        table.add_row(
            dt,
            str(_round_to_int(hourly.temp)),
            str(_round_to_int(hourly.feels_like)),
            f"{hourly.humidity}%",
            str(_round_to_int(hourly.dew_point)),
            pressure,
            conditions,
            str(hourly.uvi),
            f"{hourly.clouds}%",
            wind,
            gusts,
            f"{_round_to_int(hourly.pop * 100)}%",
            rain,
            snow,
        )

    return table


def _hourly_temp_only(
    weather: OneCallWeather, units: str, am_pm: bool, location: Location
) -> Table:
    _, _, _, temp_units = _get_units(units)
    table = Table(
        title=f"Hourly weather for {location.display_name}",
        header_style=HEADER_ROW_STYLE,
        show_lines=True,
    )
    table.add_column("Date/Time :date:")
    table.add_column(f"Temperature ({temp_units}) :thermometer:")
    table.add_column(f"Feels Like ({temp_units}) :thermometer:")

    for hourly in weather.hourly:
        dt = _format_date_time(am_pm, hourly.dt, weather.timezone_offset)

        table.add_row(
            dt,
            str(_round_to_int(hourly.temp)),
            str(_round_to_int(hourly.feels_like)),
        )

    return table


@lru_cache(maxsize=256)
def _hpa_to_in(value: float) -> float:
    return round(value / 33.863886666667, 2)


@lru_cache(maxsize=256)
def _kph_to_mph(value: float) -> float:
    return value / 1.609


@lru_cache(maxsize=256)
def _mm_to_in(value: float) -> float:
    return round(value / 25.4, 2)


@lru_cache(maxsize=256)
def _round_to_int(num: float) -> int:
    return round(num)


def _validate_units(units: str) -> None:
    if units not in ["metric", "imperial"]:
        raise ValueError("Units must either be metric or imperial")
