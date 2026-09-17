# this is a collection of AI agent tools
import json
from typing import Optional, Dict, Any
from langchain_core.tools import tool
import streamlit as st
#import proj_ai.agent.mod as mod
from . import common_mod


@tool
def tool_write_to_file(filepath: str, content: str) -> str:
    """Write contents to a file."""
    try:
        with open(common_mod.outputdir + filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to '{filepath}' ({len(content)} characters)."
    except Exception as e:
        return f"Error writing to file: {str(e)}"

@tool
def tool_read_from_file(filename: str) -> str:
    """Read and return the contents of a file."""
    try:
        with open(common_mod.inputdir + filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File '{common_mod.inputdir} + {filename}' not found."
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON in file - {str(e)}"
    except Exception as e:
        return f"Error reading JSON: {str(e)}"

@tool
def tool_get_city_coordinates(city: str) -> dict:
    """Look up the latitude and longitude for a city name using Open-Meteo geocoding.

    Args:
        city: City name, optionally with a country, e.g. "Tokyo" or "Paris, France".

    Returns:
        The first matching result's name, latitude, longitude, country, and timezone.
    """
    import httpx

    params = {"name": city, "count": 1, "language": "en", "format": "json"}
    with httpx.Client(timeout=10) as client:
        resp = client.get("https://geocoding-api.open-meteo.com/v1/search", params=params)
        resp.raise_for_status()
        data = resp.json()

    results = data.get("results") or []
    if not results:
        return {"error": f"No location found for '{city}'"}
    r = results[0]
    return {
        "name": r.get("name"),
        "country": r.get("country"),
        "admin1": r.get("admin1"),
        "latitude": r.get("latitude"),
        "longitude": r.get("longitude"),
        "timezone": r.get("timezone"),
    }

@tool
def tool_get_weather(city: str) -> Optional[Dict[str, Any]]:
    """
    Fetches current weather information for a given city.

    Args:
        city: The name of the city (e.g., "London", "Tokyo").

    Returns:
        A dictionary containing parsed weather data if successful, otherwise None.
    """
    import requests,os
    from dotenv import load_dotenv
    _=load_dotenv()

    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    try:
        WEATHER_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
    except Exception as e:
        return f"Error: {str(e)}"

    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric"                                                                 # Use 'imperial' for Fahrenheit, 'metric' for Celsius
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()                                                        # Raises an HTTPError for bad status codes (4xx or 5xx)
        data = response.json()

        
        weather_info = {                                                                   # Structure the useful data from the API's complex payload
            "city": data.get("name"),
            "country": data.get("sys", {}).get("country"),
            "description": data.get("weather", [{}])[0].get("description").capitalize(),
            "temperature": data.get("main", {}).get("temp"), # Temperature in Celsius
            "feels_like": data.get("main", {}).get("feels_like"),
            "humidity": data.get("main", {}).get("humidity")
        }
        return weather_info

    except requests.exceptions.HTTPError as e:
        # Handle API specific errors (e.g., 404 city not found, 401 invalid key)
        if response.status_code == 404:
            print(f"🚫 Error: City '{city}' not found.")
        elif response.status_code == 401:
            print("🔑 API Error: Invalid or expired API key.")
        else:
            print(f"📡 HTTP Error fetching weather data: {e}")
        return None
    except requests.exceptions.RequestException as e:
        # Handle network errors (e.g., no internet connection)
        print(f"🌐 Connection Error: Could not connect to the weather API endpoint. Check your network connection.")
        return None
AGENT_TOOLS = [tool_write_to_file,tool_read_from_file,tool_get_city_coordinates,tool_get_weather]