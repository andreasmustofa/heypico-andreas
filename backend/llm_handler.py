import os
import requests
import re
from typing import Dict, Any
from dotenv import load_dotenv
import ollama  # pip install ollama

load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def is_location_query(prompt: str) -> bool:
    """Simple intent detection: keywords for places/food/etc."""
    patterns = [r'where.*(eat|go|find|stay)', r'(restaurant|cafe|hotel).*near', r'directions to']
    return any(re.search(pattern, prompt.lower()) for pattern in patterns)

def query_llm(prompt: str, model: str = "llama3:8b") -> str:
    """Query Ollama LLM; supports streaming if needed."""
    client = ollama.Client(host=OLLAMA_URL)
    response = client.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

def refine_search_query(prompt: str) -> str:
    """Use LLM to refine user prompt into a Places API query."""
    refine_prompt = f"Extract a concise Google Places search query from: '{prompt}'. E.g., 'sushi restaurants in Tokyo'. Output only the query."
    return query_llm(refine_prompt).strip()