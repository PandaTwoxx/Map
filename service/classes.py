import uuid
from flask_login import UserMixin


class LocationDetails:
    lon = ""
    lat = ""

    def __init__(self, lon, lat) -> None:
        self.lon = lon
        self.lat = lat


class Location:
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
    id = ""
    email = ""
    username = ""
    password = ""
    firstname = ""
    lastname = ""
    locations = [Location]

    def __init__(self, un, e, p, fn, ln, location: Location = None) -> None:
        self.username = un
        self.email = e
        self.password = p
        self.firstname = fn
        self.lastname = ln
        self.locations = [Location]
        self.id = uuid.uuid4().hex

    def get_id(self):
        return self.id
