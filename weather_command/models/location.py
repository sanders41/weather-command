from camel_converter.pydantic_base import CamelBase


class Location(CamelBase):
    display_name: str
    lat: float
    lon: float
