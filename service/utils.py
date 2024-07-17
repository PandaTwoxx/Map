import uuid
from werkzeug.security import generate_password_hash
import requests
from service.classes import User, Coordinate
from requests.structures import CaseInsensitiveDict
import os
import json
from dotenv import load_dotenv


load_dotenv()

geocoding_api_key = os.getenv("GEO_CODING_API")


def keygen(hash=uuid.uuid4().hex):
    """
    Generates a key for the User to use
    """
    return generate_password_hash(hash)


def geo_code(address: str):
    url = f"https://api.geoapify.com/v1/geocode/search?text={address.replace(' ', '%20')}&apiKey={geocoding_api_key}"

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"

    resp = requests.get(url, headers=headers)
    file = json.loads(resp.text)

    
    first_feature = file['features'][0]
    if resp.status_code == 200:
        coordinate = Coordinate(
            lon=first_feature['properties']['lon'],
            lat=first_feature['properties']['lat'],
        )
        return coordinate
    else:
        return None
