
import os
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from dotenv import load_dotenv
from llm_handler import is_location_query, query_llm, refine_search_query
from maps_handler import search_places, generate_map_embed, generate_directions_link

load_dotenv()

# Unify Google Maps key env var name
GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_KEY") or os.getenv("GOOGLE_MAPS_API_KEY")
if not GOOGLE_MAPS_KEY:
    raise RuntimeError("GOOGLE_MAPS_KEY not set in environment.")

app = FastAPI(title="Local LLM Maps Chat API")

# CORS for Open WebUI and dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting (default: 20/min per IP)
limiter = Limiter(key_func=get_remote_address, default_limits=["20/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

class ChatRequest(BaseModel):
    prompt: str
    user_location: str = ""  # Optional: e.g., "New York, NY"

@app.post("/chat")
@limiter.limit("5/minute")
async def chat(request: ChatRequest):
    try:
        prompt = request.prompt
        response = query_llm(prompt)
        if is_location_query(prompt):
            search_q = refine_search_query(prompt)
            places_data = search_places(search_q, request.user_location)
            if places_data and places_data["places"]:
                place = places_data["places"][0]
                map_embed = generate_map_embed(place["lat"], place["lng"])
                directions_link = generate_directions_link(request.user_location or "current location", place)
                response += f"\n\nTop spot: {place['name']} ({place.get('rating','-')}⭐)\n{map_embed}\n[Directions]({directions_link})"
            else:
                response += "\nNo places found—try a different query!"
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Google Maps API endpoints for Open WebUI integration ---

@app.get("/search")
@limiter.limit("20/minute")
def search_endpoint(query: str = Query(..., min_length=1)):
    """Google Places Text Search (max 5 results)"""
    import requests
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": GOOGLE_MAPS_KEY}
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Google Places API error")
    data = resp.json()
    results = []
    for place in data.get("results", [])[:5]:
        name = place.get("name")
        address = place.get("formatted_address")
        place_id = place.get("place_id")
        location = place.get("geometry", {}).get("location", {})
        lat = location.get("lat")
        lng = location.get("lng")
        maps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
        embed_url = f"https://www.google.com/maps/embed/v1/place?key={GOOGLE_MAPS_KEY}&q=place_id:{place_id}"
        results.append({
            "name": name,
            "address": address,
            "place_id": place_id,
            "lat": lat,
            "lng": lng,
            "maps_link": maps_link,
            "embed_url": embed_url,
        })
    return {"results": results}

@app.get("/directions")
@limiter.limit("20/minute")
def directions_endpoint(origin: str = Query(...), destination: str = Query(...)):
    """Google Directions API (overview_polyline + maps_link)"""
    import requests
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {"origin": origin, "destination": destination, "key": GOOGLE_MAPS_KEY}
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Google Directions API error")
    data = resp.json()
    if not data.get("routes"):
        raise HTTPException(status_code=404, detail="No route found")
    route = data["routes"][0]
    overview_polyline = route.get("overview_polyline", {}).get("points")
    maps_link = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}"
    return {"overview_polyline": overview_polyline, "maps_link": maps_link}

from fastapi.responses import HTMLResponse
@app.get("/embed/{place_id}", response_class=HTMLResponse)
@limiter.limit("20/minute")
def embed_endpoint(place_id: str):
    embed_url = f"https://www.google.com/maps/embed/v1/place?key={GOOGLE_MAPS_KEY}&q=place_id:{place_id}"
    html = f"""
    <html>
      <body style='margin:0;padding:0;'>
        <iframe width='100%' height='400' frameborder='0' style='border:0' src='{embed_url}' allowfullscreen></iframe>
      </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}