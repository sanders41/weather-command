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

## Useage

First an API key is needed from [OpenWeather](https://openweathermap.org/), A free account is all that
is needed. Once you have your API key create an environment variable named `OPEN_WEATHER_API_KEY` that
constains your API key.

```sh
export OPEN_WEATHER_API_KEY=your-api-key
```

To get the weather for a city:

```sh
weather-command city seattle
```

### Arguments

* [HOW]: How to get the weather. Accepted values are city and zip. [default: city]
* [CITY_ZIP]: The name of the city or zip code for which the weather should be retrieved. If the
first argument is 'city' this should be the name of the city, or if 'zip' it should be the zip
code. [required]

### Options

* -u, --units: The units to use. Accepted values are metricand imperial. [default: metric]
* -s, --state-code: The name of the state where the city is located.
* -c, --country-code: The country code where the city is located.
* --am-pm: If this flag is set the times will be displayed in 12 hour format, otherwise times
will be 24 hour format.
* -t, --temp-only: If this flag is set only tempatures will be displayed.
* --terminal_width: Allows for overriding the default terminal width.
* --install-completion [bash|zsh|fish|powershell|pwsh]: Install completion for the specified shell.
* --show-completion [bash|zsh|fish|powershell|pwsh]: Show completion for the specified shell, to
copy it or customize the installation.
* --help: Show this message and exit.

## Contributing

Contributions to this project are welcome. If you are interesting in contributing please see our [contributing guide](CONTRIBUTING.md)
