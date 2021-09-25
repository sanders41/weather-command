from typing import Optional

from dotenv import load_dotenv
from typer import Argument, BadParameter, Option, Typer

from weather_command._builder import show_current

load_dotenv()

app = Typer()


@app.command()
def main(
    how: str = Argument("city", help="How to get the weather. Accepted values are city and zip."),
    city_zip: str = Argument(
        ...,
        help="The name of the city or zip code for which the weather should be retrieved. If the first argument is 'city' this should be the name of the city, or if 'zip' it should be the zip code.",
    ),
    units: str = Option(
        "metric", "--units", "-u", help="The units to use. Accepted values are metric and imperial."
    ),
    state_code: Optional[str] = Option(
        None, "--state-code", "-s", help="The name of the state where the city is located."
    ),
    country_code: Optional[str] = Option(
        None, "--country-code", "-c", help="The country code where the city is located."
    ),
    am_pm: bool = Option(
        False,
        "--am-pm",
        help="If this flag is set the times will be displayed in 12 hour format, otherwise times will be 24 hour format.",
    ),
    temp_only: bool = Option(
        False, "--temp-only", "-t", help="If this flag is set only tempatures will be displayed."
    ),
    terminal_width: Optional[int] = Option(
        None, "--terminal_width", help="Allows for overriding the default terminal width."
    ),
) -> None:
    _validate_how(how)
    _validate_units(units)

    show_current(
        how,
        city_zip=city_zip,
        units=units,
        state_code=state_code,
        country_code=country_code,
        am_pm=am_pm,
        temp_only=temp_only,
        terminal_width=terminal_width,
    )


def _validate_how(how: str) -> None:
    if how not in ("city", "zip"):
        raise BadParameter("The first argument must either be 'city' or 'zip'")


def _validate_units(units: str) -> None:
    if units not in ("metric", "imperial"):
        raise BadParameter("Only 'metric' and 'imperial' are accepted for '-u/--units'")


if __name__ == "__main__":
    app()
