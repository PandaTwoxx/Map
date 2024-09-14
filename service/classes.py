"""UserMixin module"""
from flask_login import UserMixin


class LocationDetails:
    """holds lon and lat variables
    """
    lon = ""
    lat = ""

    def __init__(self, lon, lat) -> None:
        self.lon = lon
        self.lat = lat


class Location:
    """Holds Location data
    """
    name = ""
    location = LocationDetails
    address = ""
    description = ""

    def __init__(self, name, description, address, location=None) -> None:
        self.name = name
        self.location = location
        self.address = address
        self.description = description


class User(UserMixin):
    """User object"""
    id = ""
    email = ""
    username = ""
    password = ""
    firstname = ""
    lastname = ""
    locations = [Location]

    def __init__(self, un, e, p, fn, ln) -> None:
        self.username = un
        self.email = e
        self.password = p
        self.firstname = fn
        self.lastname = ln
        self.locations = [Location]

    def get_id(self):
        return self.id
