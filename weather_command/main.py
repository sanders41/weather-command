import asyncio
from enum import Enum
from typing import Coroutine, List, Union

from typer import Argument, Exit, Option, Typer, echo

from weather_command import settings_commands
from weather_command._builder import show_current, show_daily, show_hourly
from weather_command._cache import Cache
from weather_command._config import console, load_settings
from weather_command._location import build_location_url, get_location_details
from weather_command._utils import build_weather_url
from weather_command._weather import get_current_weather, get_one_call_weather

__version__ = "6.1.0"

app = Typer()
app.add_typer(settings_commands.app, name="settings", help="Manage saved settings.")


class ForecastType(str, Enum):
    CURRENT = "current"
    DAILY = "daily"
    HOURLY = "hourly"


class How(str, Enum):
    CITY = "city"
    ZIP = "zip"


async def _preload_cache(
    how: str,
    city_zip: str,
    state_code: Union[str, None],
    country_code: Union[str, None],
    units: str,
) -> None:
    with console.status("Getting weather..."):
        retrieve: List[Coroutine] = []
        location_url = build_location_url(how, city_zip, state_code, country_code)
        cache = Cache()
        cache_hit = cache.get(location_url)
        if cache_hit:
            if cache_hit.location:
                location = cache_hit.location
            else:  # pragma: no cover
                # This is a fail safe. It should only be possible to get here if someone manually
                # modified the cache file.
                location = get_location_details(
                    how="zip", city_zip=city_zip, state=state_code, country=country_code
                )

            if not cache_hit.current_weather:
                url = build_weather_url(
                    forecast_type="current",
                    units=units,
                    lon=location.lon,
                    lat=location.lat,
                )
                retrieve.append(get_current_weather(url, location_url))
            if not cache_hit.one_call_weather:
                url = build_weather_url(
                    forecast_type="daily", units=units, lon=location.lon, lat=location.lat
                )
                retrieve.append(get_one_call_weather(url, location_url))
        else:
            location = get_location_details(
                how=how, city_zip=city_zip, state=state_code, country=country_code
            )

            url = build_weather_url(
                forecast_type="current", units=units, lon=location.lon, lat=location.lat
            )
            retrieve.append(get_current_weather(url, location_url))

            url = build_weather_url(
                forecast_type="daily", units=units, lon=location.lon, lat=location.lat
            )
            retrieve.append(get_one_call_weather(url, location_url))

        if retrieve:
            await asyncio.gather(*retrieve)


async def _runner(
    how: str,
    city_zip: str,
    state_code: Union[str, None],
    country_code: Union[str, None],
    imperial: bool,
    am_pm: bool,
    forecast_type: ForecastType,
    temp_only: bool,
    pager: bool,
    clear_cache: bool,
    terminal_width: Union[int, None],
) -> None:
    settings = load_settings()

    if not imperial and settings.imperial is not None:
        units = "imperial" if settings.imperial else "metric"
    else:
        units = "imperial" if imperial else "metric"

    if not temp_only and settings.temp_only is not None:
        temp_only_choice = settings.temp_only
    else:
        temp_only_choice = temp_only

    if not am_pm and settings.am_pm is not None:
        am_pm_choice = settings.am_pm
    else:
        am_pm_choice = am_pm

    if clear_cache:
        cache = Cache()
        cache.clear()

    if not clear_cache:
        await _preload_cache(how, city_zip, state_code, country_code, units)

    if forecast_type == "current":
        await show_current(
            how=how,
            city_zip=city_zip,
            units=units,
            state_code=state_code,
            country_code=country_code,
            am_pm=am_pm_choice,
            temp_only=temp_only_choice,
            pager=pager,
            terminal_width=terminal_width,
        )
    elif forecast_type == "daily":
        await show_daily(
            how=how,
            city_zip=city_zip,
            units=units,
            state_code=state_code,
            country_code=country_code,
            am_pm=am_pm_choice,
            temp_only=temp_only_choice,
            pager=pager,
            terminal_width=terminal_width,
        )
    elif forecast_type == "hourly":
        await show_hourly(
            how=how,
            city_zip=city_zip,
            units=units,
            state_code=state_code,
            country_code=country_code,
            am_pm=am_pm_choice,
            temp_only=temp_only_choice,
            pager=pager,
            terminal_width=terminal_width,
        )


@app.command()
def city(
    city: str = Argument(
        ...,
        help="The city for which the weather should be retrieved.",
    ),
    state_code: Union[str, None] = Option(
        None, "--state-code", "-s", help="The name of the state where the city is located."
    ),
    country_code: Union[str, None] = Option(
        None,
        "--country-code",
        "-c",
        help="The country code where the city is located.",
    ),
    imperial: bool = Option(
        False,
        "--imperial",
        "-i",
        help="If this flag is used the units will be imperial, otherwise units will be metric.",
    ),
    am_pm: bool = Option(
        False,
        "--am-pm",
        help="If this flag is set the times will be displayed in 12 hour format, otherwise times will be 24 hour format.",
    ),
    forecast_type: ForecastType = Option(
        ForecastType.CURRENT,
        "--forecast-type",
        "-f",
        help="The type of forecast to display.",
    ),
    temp_only: bool = Option(
        False, "--temp-only", "-t", help="If this flag is set only tempatures will be displayed."
    ),
    pager: bool = Option(False, "--pager", "-p", help="Display the results in a pager."),
    clear_cache: bool = Option(False, help="Clear the cache data before running."),
    terminal_width: Union[int, None] = Option(
        None, help="Allows for overriding the default terminal width."
    ),
) -> None:
    """Get the weather by city."""
    asyncio.run(
        _runner(
            how="city",
            city_zip=city,
            state_code=state_code,
            country_code=country_code,
            imperial=imperial,
            am_pm=am_pm,
            forecast_type=forecast_type,
            temp_only=temp_only,
            pager=pager,
            clear_cache=clear_cache,
            terminal_width=terminal_width,
        )
    )


@app.command()
def zip(
    zip_code: str = Argument(
        ...,
        help="The zip code for which the weather should be retrieved.",
    ),
    state_code: Union[str, None] = Option(
        None, "--state-code", "-s", help="The name of the state where the city is located."
    ),
    country_code: Union[str, None] = Option(
        None,
        "--country-code",
        "-c",
        help="The country code where the city is located.",
    ),
    imperial: bool = Option(
        False,
        "--imperial",
        "-i",
        help="If this flag is used the units will be imperial, otherwise units will be metric.",
    ),
    am_pm: bool = Option(
        False,
        "--am-pm",
        help="If this flag is set the times will be displayed in 12 hour format, otherwise times will be 24 hour format.",
    ),
    forecast_type: ForecastType = Option(
        ForecastType.CURRENT,
        "--forecast-type",
        "-f",
        help="The type of forecast to display.",
    ),
    temp_only: bool = Option(
        False, "--temp-only", "-t", help="If this flag is set only tempatures will be displayed."
    ),
    pager: bool = Option(False, "--pager", "-p", help="Display the results in a pager."),
    clear_cache: bool = Option(False, help="Clear the cache data before running."),
    terminal_width: Union[int, None] = Option(
        None, help="Allows for overriding the default terminal width."
    ),
) -> None:
    """Get the weather by zip code."""
    asyncio.run(
        _runner(
            how="zip",
            city_zip=zip_code,
            state_code=state_code,
            country_code=country_code,
            imperial=imperial,
            am_pm=am_pm,
            forecast_type=forecast_type,
            temp_only=temp_only,
            pager=pager,
            clear_cache=clear_cache,
            terminal_width=terminal_width,
        )
    )


@app.callback(invoke_without_command=True)
def main(
    version: Union[bool, None] = Option(
        None,
        "--version",
        "-v",
        is_eager=True,
        help="Show the installed version",
    ),
) -> None:
    if version:
        echo(__version__)
        raise Exit()


if __name__ == "__main__":
    app()
