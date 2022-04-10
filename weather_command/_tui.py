from __future__ import annotations

from asyncio import gather
from datetime import datetime
from typing import NamedTuple

from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.app import App
from textual.widget import Widget
from textual.widgets import Footer, Header, ScrollView

from weather_command._builder import build_url, current_weather_all, daily_all, hourly_all
from weather_command._cache import Cache
from weather_command._location import get_location_details
from weather_command._weather import get_current_weather, get_one_call_weather
from weather_command.models.location import Location


class PanelCache(NamedTuple):
    panel: Panel


class _BaseWeatherPanel(Widget):
    def __init__(
        self,
        location: Location,
        how: str,
        city_zip: str,
        units: str,
        am_pm: bool,
        state: str | None = None,
        country: str | None = None,
    ) -> None:
        self.location = location
        self.how = how
        self.city_zip = city_zip
        self.state = state
        self.country = country
        self.units = units
        self.am_pm = am_pm
        self.panel_cache: PanelCache | None = None
        self.panel = Panel("Loading...")

        super().__init__()

    async def build_panel(self) -> None:
        ...  # pragma: no cover

    def clear_cache(self) -> None:
        self.panel_cache = None

    async def on_mount(self) -> None:
        await self.build_panel()
        self.refresh(layout=True)

    def render(self) -> Panel:
        return self.panel


class WeatherHeader(Header):
    def render(self) -> RenderableType:
        """Override default render to display a different icon."""
        header_table = Table.grid(padding=(0, 1), expand=True)
        header_table.style = self.style
        header_table.add_column(justify="left", ratio=0, width=8)
        header_table.add_column("title", justify="center", ratio=1)
        header_table.add_column("clock", justify="right", width=8)
        header_table.add_row("🌞", self.full_title, self.get_clock() if self.clock else "")
        header: RenderableType
        header = Panel(header_table, style=self.style) if self.tall else header_table
        return header


class WeatherFooter(Footer):
    def make_key_text(self) -> Text:
        """Override default to change color."""
        text = Text(
            style="black on sky_blue2",
            no_wrap=True,
            overflow="ellipsis",
            justify="left",
            end="",
        )
        for binding in self.app.bindings.shown_keys:
            key_display = (
                binding.key.upper() if binding.key_display is None else binding.key_display
            )
            hovered = self.highlight_key == binding.key
            key_text = Text.assemble(
                (f" {key_display} ", "reverse" if hovered else "default on default"),
                f" {binding.description} ",
                meta={"@click": f"app.press('{binding.key}')", "key": binding.key},
            )
            text.append_text(key_text)
        return text


class CurrentWeather(_BaseWeatherPanel):
    def __init__(
        self,
        location: Location,
        how: str,
        city_zip: str,
        units: str,
        am_pm: bool,
        state: str | None = None,
        country: str | None = None,
    ) -> None:
        super().__init__(
            location=location,
            how=how,
            city_zip=city_zip,
            units=units,
            am_pm=am_pm,
            state=state,
            country=country,
        )

    async def build_panel(self) -> None:
        if self.panel_cache:
            self.panel = self.panel_cache.panel
            return None

        url = build_url(
            forecast_type="current",
            units=self.units,
            lon=self.location.lon,
            lat=self.location.lat,
        )
        current_weather = await get_current_weather(url, self.how, self.city_zip)

        table = current_weather_all(
            current_weather,
            self.units,
            self.am_pm,
            self.location,
            False,
        )
        self.panel = Panel(table, title="Current Weather")
        self.panel_cache = PanelCache(panel=self.panel)


class DailyWeather(_BaseWeatherPanel):
    def __init__(
        self,
        location: Location,
        how: str,
        city_zip: str,
        units: str,
        am_pm: bool,
        state: str | None = None,
        country: str | None = None,
    ) -> None:
        super().__init__(
            location=location,
            how=how,
            city_zip=city_zip,
            units=units,
            am_pm=am_pm,
            state=state,
            country=country,
        )

    async def build_panel(self) -> None:
        if self.panel_cache:
            self.panel = self.panel_cache.panel
            return None

        url = build_url(
            forecast_type="daily", units=self.units, lon=self.location.lon, lat=self.location.lat
        )
        one_call_weather = await get_one_call_weather(url, self.how, self.city_zip)
        table = daily_all(one_call_weather, self.units, self.am_pm, self.location, False)
        self.panel = Panel(table, title="Daily Weather")
        self.panel_cache = PanelCache(panel=self.panel)


class HourlyWeather(_BaseWeatherPanel):
    def __init__(
        self,
        location: Location,
        how: str,
        city_zip: str,
        units: str,
        am_pm: bool,
        state: str | None = None,
        country: str | None = None,
    ) -> None:
        super().__init__(
            location=location,
            how=how,
            city_zip=city_zip,
            units=units,
            am_pm=am_pm,
            state=state,
            country=country,
        )

    async def build_panel(self) -> None:
        if self.panel_cache:
            self.panel = self.panel_cache.panel
            return None

        url = build_url(
            forecast_type="daily", units=self.units, lon=self.location.lon, lat=self.location.lat
        )
        one_call_weather = await get_one_call_weather(url, self.how, self.city_zip)
        table = hourly_all(one_call_weather, self.units, self.am_pm, self.location, False)
        self.panel = Panel(table, title="Hourly Weather")
        self.panel_cache = PanelCache(panel=self.panel)


class WeatherApp(App):
    how: str
    city_zip: str
    state: str | None = None
    country: str | None = None
    forecast_type: str
    units: str
    am_pm: bool

    async def on_load(self) -> None:
        await self.bind("q", "quit", "Quit", key_display="q")
        await self.bind("c", "change_view('current')", "Show Current Weather", key_display="c")
        await self.bind("d", "change_view('daily')", "Show Daily Weather", key_display="d")
        await self.bind("h", "change_view('hourly')", "Show Hourly weather", key_display="h")
        await self.bind("r", "reload", "Reload", key_display="r")

    async def action_change_view(self, view: str) -> None:
        if view == "current":
            await self.weather_view.update(self.current)  # type: ignore
            self.active_view = "current"
        elif view == "daily":
            await self.weather_view.update(self.daily)  # type: ignore
            self.active_view = "daily"
        elif view == "hourly":
            await self.weather_view.update(self.hourly)  # type: ignore
            self.active_view = "hourly"

    async def action_reload(self) -> None:
        self.title = "Loading..."
        Cache().clear()
        self.current.clear_cache()
        self.daily.clear_cache()
        self.hourly.clear_cache()
        await gather(
            self.current.build_panel(), self.daily.build_panel(), self.hourly.build_panel()
        )
        self.current.refresh(layout=True)
        self.daily.refresh(layout=True)
        self.hourly.refresh(layout=True)

        if self.active_view == "current":
            await self.weather_view.update(self.current)  # type: ignore
        elif self.active_view == "daily":
            await self.weather_view.update(self.daily)  # type: ignore
        elif self.active_view == "hourly":
            await self.weather_view.update(self.hourly)  # type: ignore

        self.title = _generate_title(self.location, self.am_pm)
        self.last_reload = datetime.now()

    async def timer_reload(self) -> None:
        diff = round((datetime.now() - self.last_reload).total_seconds())
        if diff >= 3595:  # Give a 5 second buffer on the hour
            await self.action_reload()
        else:
            self.last_reload = datetime.now()

    async def on_mount(self) -> None:
        self.location = await get_location_details(
            how=self.how, city_zip=self.city_zip, country=self.country
        )

        self.current = CurrentWeather(
            self.location, self.how, self.city_zip, self.units, self.am_pm, self.state, self.country
        )
        self.daily = DailyWeather(
            self.location, self.how, self.city_zip, self.units, self.am_pm, self.state, self.country
        )
        self.hourly = HourlyWeather(
            self.location, self.how, self.city_zip, self.units, self.am_pm, self.state, self.country
        )

        await gather(
            self.current.build_panel(), self.daily.build_panel(), self.hourly.build_panel()
        )

        self.active_view = "current"
        self.weather_view = ScrollView(self.current, style="black on sky_blue2")

        self.footer = WeatherFooter()
        self.header = WeatherHeader(style="black on sky_blue2", clock=False)
        self.title = _generate_title(self.location, self.am_pm)

        await self.view.dock(self.header, edge="top")
        await self.view.dock(self.footer, edge="bottom")
        await self.view.dock(self.weather_view, edge="top")

        self.last_reload = datetime.now()
        self.set_interval(3600.0, self.timer_reload)  # 1 hour


def _generate_title(location: Location, am_pm: bool) -> str:
    if am_pm:
        return f"{location.display_name} | Last Update: {datetime.now().strftime('%d-%b-%Y %I:%M:%S %p')}"

    return f"{location.display_name} | Last Update: {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}"
