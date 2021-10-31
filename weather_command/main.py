from enum import Enum
from typing import Optional

from dotenv import load_dotenv
from rich.traceback import install
from typer import Argument, Option, Typer

from weather_command._builder import show_current, show_daily, show_hourly

load_dotenv()

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
def main(
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
    terminal_width: Optional[int] = Option(
        None, "--terminal_width", help="Allows for overriding the default terminal width."
    ),
) -> None:
    units = "imperial" if imperial else "metric"

    if forecast_type == "current":
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
    elif forecast_type == "daily":
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
    elif forecast_type == "hourly":
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


if __name__ == "__main__":
    app()
