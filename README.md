# Weather Command

[![Tests Status](https://github.com/sanders41/weather-command/workflows/Testing/badge.svg?branch=main&event=push)](https://github.com/sanders41/weather-command/actions?query=workflow%3ATesting+branch%3Amain+event%3Apush)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sanders41/weather-command/main.svg)](https://results.pre-commit.ci/latest/github/sanders41/weather-command/main)
[![Coverage](https://codecov.io/github/sanders41/weather-command/coverage.svg?branch=main)](https://codecov.io/gh/sanders41/weather-command)
[![PyPI version](https://badge.fury.io/py/weather-command.svg)](https://badge.fury.io/py/weather-command)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/weather-command?color=5cc141)](https://github.com/sanders41/weather-command)

A command line weather app

## Installation

Installation with [pipx](https://github.com/pypa/pipx) is recommended.

If you are running on a non-Windows OS you can install with uvloop for more speed.

```sh
pipx install "weather-command[uvloop]"
```

uvloop is currently not supported on Windows on this platform install without uvloop.

```sh
pipx install weather-command
```

Alternatively Weather Command can be installed with pip.

```sh
# Non Windows
pip install weather-command[uvloop]

# Windows
pip install weather-command
```

## Usage

First an API key is needed from [OpenWeather](https://openweathermap.org/), A free account is all that
is needed. Once you have your API key create an environment variable named `OPEN_WEATHER_API_KEY` that
constains your API key.

```sh
export OPEN_WEATHER_API_KEY=your-api-key
```

Each time the shell is restarted this variable will be cleared. To avoid this it can be added to your
profile. For example if your shell is zsh the API key can be added to the `~/.zshenv` file. Doing this
will prevent the need to re-add the key each time the shell is started.

To get the weather for a city:

```sh
weather-command city seattle
```

Once installed you can also add aliases to your shell to make it quick to get a forecast. For example
if your shell is zsh you can add something like the following to your `~/.zshrc` file:

```sh
alias we="weather-command cli zip 98109 -i --am-pm"
alias wed="weather-command cli zip 98109 -i --am-pm -f daily"
alias weh="weather-command cli zip 98109 -i --am-pm -f hourly"
alias wet="weather-command tui zip 98109 -i --am-pm"
```

After adding this to the `~/.zshrc` you will need to restart your terminal. After that typing `we`
will get the current forecast, `wed` will get the daily forecast and `weh` will get the hourly forecast.

### Modes

Weather Command can be run in either CLI (command line interface) mode or TUI (text user interface)
mode. CLI mode will print the weather to your terminal, while TUI mode will open the weather in an
interactive terminal app.

To run in CLI mode use the `cli` command

```py
weather-command cli zip 98109 -i --am-pm
```

To run in TUI mode use the `tui` command

```py
weather-command tui zip 98109 -i --am-pm
```

## Contributing

Contributions to this project are welcome. If you are interesting in contributing please see our [contributing guide](CONTRIBUTING.md)
