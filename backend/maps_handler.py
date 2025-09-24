import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_KEY") or os.getenv("GOOGLE_MAPS_API_KEY")
BASE_URL = "https://maps.googleapis.com/maps/api"

def search_places(query: str, location: Optional[str] = None) -> Optional[Dict]:
    """
    Search for places using Google Places API (Text Search).
    Returns: Dict with places list (name, address, lat, lng, rating).
    """
    if not API_KEY:
        raise ValueError("GOOGLE_MAPS_KEY not set")
    params = {
        "query": query,
        "key": API_KEY,
    }
    if location:
        params["location"] = location
    response = requests.get(f"{BASE_URL}/place/textsearch/json", params=params)
    if response.status_code != 200:
        raise Exception(f"API error: {response.text}")
    data = response.json()
    if data.get("status") not in ("OK", "ZERO_RESULTS"):
        raise Exception(f"Places API error: {data.get('status')}")
    places = []
    for place in data.get("results", [])[:3]:
        geometry = place.get("geometry", {}).get("location", {})
        places.append({
            "name": place.get("name"),
            "address": place.get("formatted_address"),
            "lat": geometry.get("lat"),
            "lng": geometry.get("lng"),
            "rating": place.get("rating")
        })
    return {"places": places} if places else None

def generate_map_embed(lat: float, lng: float, zoom: int = 15, width: int = 600, height: int = 400) -> str:
    """
    Generate iframe embed for Google Maps Embed API.
    """
    embed_url = f"https://www.google.com/maps/embed/v1/view?key={API_KEY}&center={lat},{lng}&zoom={zoom}"
    return f'<iframe src="{embed_url}" width="{width}" height="{height}" frameborder="0" style="border:0" allowfullscreen></iframe>'

def generate_directions_link(origin: str, destination: Dict) -> str:
    """
    Link to Google Maps for directions.
    """
    dest = f"{destination['lat']},{destination['lng']}"
    return f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={dest}"