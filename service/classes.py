import uuid
from flask_login import UserMixin


class Coordinate:
    lon = ""
    lat = ""

    def __init__(self, lon, lat) -> None:
        self.lon = lon
        self.lat = lat


class Location:
    name = ""
    location = Coordinate
    description = ""

    def __init__(self, name, description, location=None) -> None:
        self.name = name
        self.location = location
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
        self.locations = [location]
        self.id = uuid.uuid4().hex

    def get_id(self):
        return self.id
