"""
Traffic API — /traffic, /weather endpoints
"""

from fastapi import APIRouter, Query
from ai.traffic_predictor import TrafficPredictor
import httpx
import os

router = APIRouter()
predictor = TrafficPredictor()


@router.get("/traffic")
async def get_traffic(
    lat: float = Query(...),
    lng: float = Query(...),
    city: str = Query("chennai"),
    horizon_minutes: int = Query(30, ge=5, le=120),
):
    """
    Predict traffic congestion at a location for the next N minutes.
    Returns a congestion level (0–1) and human-readable description.
    """
    result = predictor.predict(lat, lng, city, horizon_minutes)
    return {
        "lat": lat,
        "lng": lng,
        "city": city,
        "horizon_minutes": horizon_minutes,
        "congestion_level": result["level"],
        "description": result["description"],
        "recommended_departure": result.get("recommended_departure"),
    }


@router.get("/weather")
async def get_weather(
    lat: float = Query(...),
    lng: float = Query(...),
):
    """
    Return current weather and flood risk for routing.
    Uses OpenWeatherMap API.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY", "")
    if not api_key or api_key == "your_key_here":
        return {"error": "OpenWeatherMap API key not configured.", "flood_risk": 0.0}

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"lat": lat, "lon": lng, "appid": api_key, "units": "metric"},
        )
    data = resp.json()

    rain_1h = data.get("rain", {}).get("1h", 0)
    flood_risk = min(1.0, rain_1h / 20.0)   # >20mm/h → max flood risk

    return {
        "temp_c": data["main"]["temp"],
        "description": data["weather"][0]["description"],
        "rain_mm_1h": rain_1h,
        "flood_risk": flood_risk,
        "wind_speed": data["wind"]["speed"],
    }
