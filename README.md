# Local LLM Maps Chat API Backend

A FastAPI backend for Google Maps integration and LLM-powered chat, ready for Open WebUI or any frontend.

Build by Andreas Mustofa
https://andreasmustofa.github.io

## Features

- **/chat**: LLM-powered chat endpoint, can auto-detect location queries and return top places with Google Maps embed and directions link.
- **/search**: Google Places Text Search API, returns up to 5 places with name, address, place_id, lat, lng, maps link, and embed URL.
- **/directions**: Google Directions API, returns overview polyline and Google Maps directions link.
- **/embed/{place_id}**: Returns HTML with an iframe for Google Maps embed for a place.
- **/healthz**: Health check endpoint.
- **Rate limiting**: 20 requests/minute per IP (configurable).
- **CORS**: Allows requests from http://localhost:8080 and http://localhost:3000 (for Open WebUI integration).

## Setup

1. **Clone this repo and enter backend folder**
2. **Copy and edit environment variables:**
   ```sh
   cp .env.example .env
   # Edit .env and set your GOOGLE_MAPS_KEY and (optionally) OLLAMA_BASE_URL
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Run the server:**
   ```sh
   uvicorn main:app --reload --port 8000
   ```

## API Endpoints

### POST /chat
- **Body:** `{ "prompt": "...", "user_location": "(optional)" }`
- **Returns:** LLM response, and if location intent detected, top place with map embed and directions link.

### GET /search?query=...
- **Returns:** Up to 5 places with name, address, place_id, lat, lng, maps_link, embed_url.

### GET /directions?origin=...&destination=...
- **Returns:** Route polyline and Google Maps directions link.

### GET /embed/{place_id}
- **Returns:** HTML with Google Maps embed iframe for the place.

### GET /healthz
- **Returns:** `{ "status": "ok" }`

## How to Use with Open WebUI
- Set your Open WebUI agent to call this backend (e.g., http://localhost:8000)
- Use `/search`, `/directions`, and `/embed/{place_id}` endpoints for Google Maps integration in your UI.
- Use `/chat` for LLM-powered chat with location awareness.
- CORS is enabled for http://localhost:8080 and http://localhost:3000 by default.

## Notes
- Requires a valid Google Maps API key with Places, Directions, and Embed API enabled.
- LLM chat uses Ollama by default (see `.env.example` for OLLAMA_BASE_URL).
- Rate limiting is enabled for all endpoints.
- See `/docs` for full OpenAPI documentation.

---

MIT License
