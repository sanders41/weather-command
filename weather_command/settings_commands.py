from typing import Union

from typer import Option, Typer

from weather_command._config import Settings, TimeFormat, Units, console, load_settings

app = Typer()


@app.command()
def all(
    api_key: Union[str, None] = Option(
        None,
        prompt=True,
        hide_input=True,
        help="OpenWeather API key",
    ),
    units: Units = Option(..., prompt=True, help="Preferred units"),
    temp_only: bool = Option(..., prompt=True, help="Only display temperate"),
    time_format: TimeFormat = Option(..., prompt=True, help="Preferred time format"),
) -> None:
    """Save preferences for all settings values."""
    settings = load_settings()
    imperial = units == Units.IMPERIAL
    am_pm = time_format == TimeFormat.AMPM
    settings.api_key_file = api_key
    settings.imperial = imperial
    settings.temp_only = temp_only
    settings.am_pm = am_pm
    settings.save()
    console.print("Settings preferences successfully saved", style="green")


@app.command()
def api_key(
    api_key: Union[str, None] = Option(
        None,
        prompt=True,
        hide_input=True,
        help="OpenWeather API key",
    )
) -> None:
    """Save the OpenWeather API key. Can also be set by using the OPEN_WEATHER_API_KEY environment variable."""
    settings = load_settings()
    settings.api_key_file = api_key
    settings.save()
    console.print("API key successfully saved", style="green")


@app.command()
def delete() -> None:
    """Delete saved settings."""
    settings = Settings()
    settings.delete()
    console.print("Settings file successfully deleted", style="green")


@app.command()
def saved_settings() -> None:
    """Display saved settings."""
    settings = load_settings()
    console.print(settings.display_values)


@app.command()
def temp_only(temp_only: bool = Option(..., prompt=True, help="Only display temperate")) -> None:
    """Save preference for displaying only temperature."""
    settings = load_settings()
    settings.temp_only = temp_only
    settings.save()
    console.print("Temp only preference successfully saved", style="green")


@app.command()
def time_format(
    time_format: TimeFormat = Option(..., prompt=True, help="Preferred time format")
) -> None:
    """Save the preferred time format."""
    settings = load_settings()
    am_pm = time_format == TimeFormat.AMPM
    settings.am_pm = am_pm
    settings.save()
    console.print("Units preference successfully saved", style="green")


@app.command()
def units(units: Units = Option(..., prompt=True, help="Preferred units")) -> None:
    """Save the preferred units when displaying weather."""
    settings = load_settings()
    imperial = units == Units.IMPERIAL
    settings.imperial = imperial
    settings.save()
    console.print("Units preference successfully saved", style="green")
