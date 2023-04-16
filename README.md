# Weather Command

[![Tests Status](https://github.com/sanders41/weather-command/workflows/Testing/badge.svg?branch=main&event=push)](https://github.com/sanders41/weather-command/actions?query=workflow%3ATesting+branch%3Amain+event%3Apush)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sanders41/weather-command/main.svg)](https://results.pre-commit.ci/latest/github/sanders41/weather-command/main)
[![Coverage](https://codecov.io/github/sanders41/weather-command/coverage.svg?branch=main)](https://codecov.io/gh/sanders41/weather-command)
[![PyPI version](https://badge.fury.io/py/weather-command.svg)](https://badge.fury.io/py/weather-command)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/weather-command?color=5cc141)](https://github.com/sanders41/weather-command)

A command line weather app

## Installation

Installation with [pipx](https://github.com/pypa/pipx) is recommended.

```sh
pipx install weather-command
```

Alternatively Weather Command can be installed with pip.

```sh
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
weather city seattle
```

Once installed you can also add aliases to your shell to make it quick to get a forecast. For example
if your shell is zsh you can add something like the following to your `~/.zshrc` file:

```sh
alias we="weather zip 98109 -i --am-pm"
alias wed="weather zip 98109 -i --am-pm -f daily"
alias weh="weather zip 98109 -i --am-pm -f hourly"
```

After adding this to the `~/.zshrc` you will need to restart your terminal. After that typing `we`
will get the current forecast, `wed` will get the daily forecast and `weh` will get the hourly forecast.

## Examples

- Current Weather

![Current weather](./assets/current.png)

- Current Weather Temp Only

![Current weather temp only](./assets/current_temp_only.png)

- Daily Weather

![Daily weather](./assets/daily.png)

- Daily Weather Temp Only

![Daily weather temp only](./assets/daily_temp_only.png)

- Hourly Weather

![Hourly weather](./assets/hourly.png)

- Hourly Weather Temp Only

![Hourl weather temp only](./assets/hourly_temp_only.png)

## Settings
weather now has the ability to save settings to default certain flags. The list of possible settings can be seen with:

```sh
weather settings --help
```
## Contributing

Contributions to this project are welcome. If you are interesting in contributing please see our [contributing guide](CONTRIBUTING.md)
