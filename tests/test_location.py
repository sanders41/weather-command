import httpx
import pytest

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
@pytest.mark.usefixtures("mock_cache_dir")
def test_get_location_details(how, return_type, mock_location_data, monkeypatch):
    def mock_get_response(*args, **kwargs):
        return httpx.Response(
            200, request=httpx.Request("get", url="https://test.com"), json=return_json
        )

    if return_type == "list":
        return_json = mock_location_data
    else:
        return_json = mock_location_data[0]

    monkeypatch.setattr(httpx, "get", mock_get_response)
    response = get_location_details(how=how, city_zip="test", state="test", country="test")

    assert response.display_name == mock_location_data[0]["display_name"]
    assert response.lat == float(mock_location_data[0]["lat"])
    assert response.lon == float(mock_location_data[0]["lon"])


@pytest.mark.usefixtures("mock_cache_dir")
def test_get_location_details_cache_hit(mock_location_data, monkeypatch):
    def mock_get_response(*args, **kwargs):
        return httpx.Response(
            200, request=httpx.Request("get", url="https://test.com"), json=return_json
        )

    return_json = mock_location_data

    monkeypatch.setattr(httpx, "get", mock_get_response)
    get_location_details(
        how="zip", city_zip="test", state="test", country="test"
    )  # first run to cache
    response = get_location_details(how="zip", city_zip="test", state="test", country="test")

    assert response.display_name == mock_location_data[0]["display_name"]
    assert response.lat == float(mock_location_data[0]["lat"])
    assert response.lon == float(mock_location_data[0]["lon"])


@pytest.mark.usefixtures("mock_cache_dir")
def test_get_location_details_http_error_404(capfd, monkeypatch):
    def mock_get_response(*args, **kwargs):
        return httpx.Response(404, request=httpx.Request("get", url="https://test.com"))

    monkeypatch.setattr(httpx, "get", mock_get_response)
    with pytest.raises(SystemExit):
        get_location_details(how="city", city_zip="test")

    out, _ = capfd.readouterr()
    assert "Unable" in out


@pytest.mark.usefixtures("mock_cache_dir")
def test_get_location_details_https_error(monkeypatch):
    def mock_get_response(*args, **kwargs):
        return httpx.Response(500, request=httpx.Request("get", url="https://test.com"))

    monkeypatch.setattr(httpx, "get", mock_get_response)

    with pytest.raises(httpx.HTTPStatusError):
        get_location_details(how="city", city_zip="test")


@pytest.mark.usefixtures("mock_cache_dir")
def test_get_location_details_validation_error(capfd, monkeypatch):
    def mock_get_response(*args, **kwargs):
        return httpx.Response(200, request=httpx.Request("get", url="https://test.com"), json=data)

    monkeypatch.setattr(httpx, "get", mock_get_response)

    data = {"bad": None}
    with pytest.raises(SystemExit):
        get_location_details(how="city", city_zip="test")

    out, _ = capfd.readouterr()
    assert "Unable" in out


@pytest.mark.usefixtures("mock_cache_dir")
def test_get_location_details_empty_list(capfd, monkeypatch):
    def mock_get_response(*args, **kwargs):
        return httpx.Response(200, request=httpx.Request("get", url="https://test.com"), json=[])

    monkeypatch.setattr(httpx, "get", mock_get_response)

    with pytest.raises(SystemExit):
        get_location_details(how="zip", city_zip="12345")
        out, _ = capfd.readouterr()
        assert "Unable" in out


@pytest.mark.usefixtures("mock_cache_dir")
def test_get_location_details_error():
    with pytest.raises(UnknownSearchTypeError):
        get_location_details(how="bad", city_zip="test")
