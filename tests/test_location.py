from unittest.mock import patch

import pytest
from httpx import Request, Response

from weather_command._location import get_location_details
from weather_command.errors import UnknownSearchTypeError


@pytest.fixture
def mock_location_data():
    return [
        {
            "place_id": 260813029,
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright",
            "boundingbox": [
                "35.998145769963",
                "36.318145769963",
                "-79.973361975164",
                "-79.653361975164",
            ],
            "lat": "36.15814576996293",
            "lon": "-79.81336197516389",
            "display_name": "Greensboro, Guilford County, North Carolina, 27455, United States",
            "class": "place",
            "type": "postcode",
            "importance": 0.33499999999999996,
        }
    ]


@pytest.mark.parametrize("how", ["city", "zip"])
@pytest.mark.parametrize("return_type", ["list", "dict"])
def test_get_location_details(how, return_type, mock_location_data):
    if return_type == "list":
        return_json = mock_location_data
    else:
        return_json = mock_location_data[0]
    with patch(
        "httpx.get",
        return_value=Response(
            200, request=Request("get", url="https://test.com"), json=return_json
        ),
    ):
        response = get_location_details(how=how, city_zip="test", state="test", country="test")

    assert response.display_name == mock_location_data[0]["display_name"]
    assert response.lat == float(mock_location_data[0]["lat"])
    assert response.lon == float(mock_location_data[0]["lon"])


def test_get_location_details_error():
    with pytest.raises(UnknownSearchTypeError):
        get_location_details(how="bad", city_zip="test")
