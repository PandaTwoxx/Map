"""Modules and libraries"""
import os
import json
import requests
from requests.structures import CaseInsensitiveDict
from dotenv import load_dotenv
from service.classes import LocationDetails

load_dotenv()

geocoding_api_key = os.getenv("GEO_CODING_API")


def geo_code(address: str):
    """Uses geocoding api to get coordinates of address
    Args:
        address (str): The address

    Returns:
        dict: the format
    """
    url = f"https://api.geoapify.com/v1/geocode/search?text={address.replace(' ', '%20')}\
    &apiKey={geocoding_api_key}"

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"

    resp = requests.get(url, headers=headers, timeout=10)
    file = json.loads(resp.text)


    if resp.status_code == 200 and len(file['features']) > 0:
        first_feature = file['features'][0]
        coordinate = LocationDetails(
            lon=first_feature['properties']['lon'],
            lat=first_feature['properties']['lat'],
        )
        formatted = first_feature['properties']['formatted']
        return {"coordinate":coordinate, "formatted_address":formatted}
    else:
        return None
