import uuid
from werkzeug.security import generate_password_hash
import requests
from service.classes import User, LocationDetails
from requests.structures import CaseInsensitiveDict
import os
import json
from dotenv import load_dotenv


load_dotenv()

geocoding_api_key = os.getenv("GEO_CODING_API")


def geo_code(address: str):
    url = f"https://api.geoapify.com/v1/geocode/search?text={address.replace(' ', '%20')}&apiKey={geocoding_api_key}"

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"

    resp = requests.get(url, headers=headers)
    file = json.loads(resp.text)

    
    if resp.status_code == 200 and len(file['features']) > 0:
        first_feature = file['features'][0]
        coordinate = LocationDetails(
            lon=round(first_feature['properties']['lon'],8),
            lat=round(first_feature['properties']['lat'],8),
        )
        formatted = first_feature['properties']['formatted']
        return {"coordinate":coordinate, "formatted_address":formatted}
    else:
        return None
