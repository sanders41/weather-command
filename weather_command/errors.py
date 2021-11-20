from __future__ import annotations

import sys

from httpx import HTTPStatusError
from rich.console import Console


class MissingApiKey(Exception):
    pass


class UnknownSearchTypeError(Exception):
    pass


def check_status_error(error: HTTPStatusError, console: Console) -> None:
    if error.response.status_code == 404:
        console.print("Unable to find weather data for the specified location", style="error")
        sys.exit(1)
    raise error
