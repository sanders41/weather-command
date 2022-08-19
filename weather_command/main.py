import asyncio
from enum import Enum
from sys import platform
from typing import Optional

from rich.traceback import install
from typer import Argument, Exit, Option, Typer, echo

from weather_command._builder import show_current, show_daily, show_hourly
from weather_command._cache import Cache
from weather_command._tui import WeatherApp


def _is_uvloop_platform() -> bool:
    if platform != "win32":
        return True  # pragma: no cover

    return False  # pragma: no cover


if _is_uvloop_platform():
    try:
        import uvloop
    except ImportError:  # pragma: no cover
        pass

__version__ = "3.2.6"

install()
app = Typer()


class ForecastType(str, Enum):
    CURRENT = "current"
    DAILY = "daily"
    HOURLY = "hourly"


class How(str, Enum):
    CITY = "city"
    ZIP = "zip"


@app.command()
def cli(
    how: How = Argument(
        "city",
        help="How to get the weather.",
    ),
    city_zip: str = Argument(
        ...,
        help="The name of the city or zip code for which the weather should be retrieved. If the first argument is 'city' this should be the name of the city, or if 'zip' it should be the zip code.",
    ),
    state_code: Optional[str] = Option(
        None, "--state-code", "-s", help="The name of the state where the city is located."
    ),
    country_code: Optional[str] = Option(
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
    terminal_width: Optional[int] = Option(
        None, help="Allows for overriding the default terminal width."
    ),
) -> None:
    """Run in CLI mode."""

    if _is_uvloop_platform():
        try:
            uvloop.install()
        except NameError:  # pragma: no cover
            pass

    if clear_cache:
        cache = Cache()
        cache.clear()

    units = "imperial" if imperial else "metric"

    if forecast_type == "current":
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


@app.callback(invoke_without_command=True)
def main(
    version: Optional[bool] = Option(
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


@app.command()
def tui(
    how: How = Argument(
        "city",
        help="How to get the weather.",
    ),
    city_zip: str = Argument(
        ...,
        help="The name of the city or zip code for which the weather should be retrieved. If the first argument is 'city' this should be the name of the city, or if 'zip' it should be the zip code.",
    ),
    state_code: Optional[str] = Option(
        None, "--state-code", "-s", help="The name of the state where the city is located."
    ),
    country_code: Optional[str] = Option(
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
    clear_cache: bool = Option(False, help="Clear the cache data before running."),
) -> None:
    """Run in TUI mode."""

    if clear_cache:
        cache = Cache()
        cache.clear()

    WeatherApp.how = how
    WeatherApp.city_zip = city_zip
    WeatherApp.state = state_code
    WeatherApp.country = country_code
    WeatherApp.forecast_type = forecast_type
    WeatherApp.units = "imperial" if imperial else "metric"
    WeatherApp.am_pm = am_pm
    WeatherApp.run()


if __name__ == "__main__":
    app()
