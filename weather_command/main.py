import asyncio
from enum import Enum
from sys import platform
from typing import Union

from rich.traceback import install
from typer import Argument, Exit, Option, Typer, echo

from weather_command._builder import show_current, show_daily, show_hourly
from weather_command._cache import Cache
from weather_command._tui import WeatherApp


def _is_uvloop_platform() -> bool:
    if platform != "win32":
        return True  # pragma: no cover

    return False  # pragma: no cover


__version__ = "4.0.1"

install()
app = Typer()


class ForecastType(str, Enum):
    CURRENT = "current"
    DAILY = "daily"
    HOURLY = "hourly"


class How(str, Enum):
    CITY = "city"
    ZIP = "zip"


def _runner(
    how: str,
    city_zip: str,
    state_code: Union[str, None],
    country_code: Union[str, None],
    imperial: bool,
    am_pm: bool,
    forecast_type: ForecastType,
    temp_only: bool,
    clear_cache: bool,
    tui: bool,
    terminal_width: Union[int, None],
) -> None:
    if clear_cache:
        cache = Cache()
        cache.clear()

    units = "imperial" if imperial else "metric"

    if _is_uvloop_platform():
        try:
            import uvloop

            uvloop.install()
        except ImportError:  # pragma: no cover
            pass
        except NameError:  # pragma: no cover
            pass

    if tui:
        WeatherApp.how = how
        WeatherApp.city_zip = city_zip
        WeatherApp.state = state_code
        WeatherApp.country = country_code
        WeatherApp.forecast_type = forecast_type
        WeatherApp.units = units
        WeatherApp.am_pm = am_pm
        WeatherApp.run()
    elif forecast_type == "current":
        asyncio.run(
            show_current(
                how=how,
                city_zip=city_zip,
                units=units,
                state_code=state_code,
                country_code=country_code,
                am_pm=am_pm,
                temp_only=temp_only,
                terminal_width=terminal_width,
            )
        )
    elif forecast_type == "daily":
        asyncio.run(
            show_daily(
                how=how,
                city_zip=city_zip,
                units=units,
                state_code=state_code,
                country_code=country_code,
                am_pm=am_pm,
                temp_only=temp_only,
                terminal_width=terminal_width,
            )
        )
    elif forecast_type == "hourly":
        asyncio.run(
            show_hourly(
                how=how,
                city_zip=city_zip,
                units=units,
                state_code=state_code,
                country_code=country_code,
                am_pm=am_pm,
                temp_only=temp_only,
                terminal_width=terminal_width,
            )
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
    clear_cache: bool = Option(False, help="Clear the cache data before running."),
    tui: bool = Option(False, help="Run in TUI mode."),
    terminal_width: Union[int, None] = Option(
        None, help="Allows for overriding the default terminal width."
    ),
) -> None:
    """Get the weather by city."""
    _runner(
        how="city",
        city_zip=city,
        state_code=state_code,
        country_code=country_code,
        imperial=imperial,
        am_pm=am_pm,
        forecast_type=forecast_type,
        temp_only=temp_only,
        clear_cache=clear_cache,
        tui=tui,
        terminal_width=terminal_width,
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
    clear_cache: bool = Option(False, help="Clear the cache data before running."),
    tui: bool = Option(False, help="Run in TUI mode."),
    terminal_width: Union[int, None] = Option(
        None, help="Allows for overriding the default terminal width."
    ),
) -> None:
    """Get the weather by zip code."""
    _runner(
        how="zip",
        city_zip=zip_code,
        state_code=state_code,
        country_code=country_code,
        imperial=imperial,
        am_pm=am_pm,
        forecast_type=forecast_type,
        temp_only=temp_only,
        clear_cache=clear_cache,
        tui=tui,
        terminal_width=terminal_width,
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
