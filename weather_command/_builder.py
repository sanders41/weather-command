from __future__ import annotations

from datetime import datetime, timedelta

from rich.console import Console
from rich.table import Table

from weather_command._config import BASE_URL, apppend_api_key
from weather_command._weather import WeatherIcons, get_current_weather


def show_current_weather_by_city(
    city: str,
    *,
    state_code: str | None = None,
    country_code: str | None = None,
    units: str = "metric",
    am_pm: bool = False,
) -> None:
    url = f"{BASE_URL}?q={city}&units={units}"

    if state_code:
        url = f"{url}&state_code={state_code}"

    if country_code:
        url = f"{url}&country_code={country_code}"

    url = apppend_api_key(url)

    console = Console()

    with console.status("Getting weather..."):
        current_weather = get_current_weather(url)

    temp_unit = "C" if units == "metric" else "F"
    speed_unit = "kph" if units == "metric" else "mph"
    precip_unit = "cm" if units == "metric" else "in"
    main_condition = current_weather.weather[0].main
    weather_icon = WeatherIcons.get_value(main_condition)
    if weather_icon:
        main_condition += f" {weather_icon}"
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
        main_condition,
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

    console.print(table)
