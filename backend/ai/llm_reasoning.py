"""
LLM Reasoning — uses a language model to generate human-readable route explanations
in the style of an experienced local auto driver.
"""

import httpx
import os


DRIVER_PERSONA = """You are an experienced auto driver in South India with 15 years on the road.
You know every shortcut, every pothole, every school zone, and every flood-prone stretch.
When explaining route choices, speak naturally and practically — like you're giving advice to a friend.
Keep it short (2–3 sentences). Mention specific local knowledge where relevant."""


async def explain_route(route: dict, city: str) -> str:
    """
    Generate a natural language explanation for why this route was chosen.
    Uses the Anthropic API with the driver persona.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        return _fallback_explanation(route)

    prompt = (
        f"City: {city.title()}\n"
        f"Route distance: {route['distance_km']} km\n"
        f"ETA: {route['eta_minutes']} minutes\n"
        f"Road quality score: {route['road_quality_score']:.0%}\n"
        f"Driver satisfaction score: {route['driver_score']:.0%}\n"
        f"Safety score: {route['safety_score']:.0%}\n\n"
        "As an experienced local auto driver, briefly explain why this route was chosen over the shortest path."
    )

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 150,
                    "system": DRIVER_PERSONA,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
        data = resp.json()
        return data["content"][0]["text"].strip()
    except Exception as e:
        return _fallback_explanation(route)


def _fallback_explanation(route: dict) -> str:
    quality = route.get("road_quality_score", 0.5)
    driver = route.get("driver_score", 0.5)
    if quality > 0.75 and driver > 0.75:
        return "This road is well-maintained and preferred by local drivers for smooth travel."
    elif quality > 0.6:
        return "Decent road surface with moderate traffic — a reliable choice."
    else:
        return "Fastest available route given current road conditions."
