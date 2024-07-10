import uuid
from werkzeug.security import generate_password_hash
import requests
from flask import flash
from service.classes import User, Coordinate
from requests.structures import CaseInsensitiveDict
import os
from dotenv import load_dotenv


load_dotenv()

geocoding_api_key = os.getenv("GEO_CODING_API")


def keygen(hash=uuid.uuid4().hex):
    """
    Generates a key for the User to use
    """
    return generate_password_hash(hash)


def geo_code(address: str):
    url = f"https://api.geoapify.com/v1/geocode/search?text={address.replace('+', '%20')}&apiKey={geocoding_api_key}"

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"

    resp = requests.get(url, headers=headers)

    if resp.status_code == 200:
        coordinate = Coordinate(
            lon=resp.features[0].properties["lon"],
            lat=resp.features[0].properties["lat"],
        )
        return coordinate
    else:
        flash("Bad address or server")
        return None
