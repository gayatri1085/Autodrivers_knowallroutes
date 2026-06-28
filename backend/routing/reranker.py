"""
Route Re-ranker — applies AI scoring on top of graph-generated candidate routes.
"""

import asyncio
from typing import Optional


LABEL_HIGHLIGHTS = {
    0: [
        "Preferred by local auto drivers",
        "Smoother road surface",
        "Avoids known congestion points",
    ],
    1: [
        "Fastest ETA",
        "Main arterial roads",
    ],
    2: [
        "Scenic alternative",
        "Less traffic at peak hours",
        "Good for two-wheelers",
    ],
}


async def rerank_routes(
    candidates: list[dict],
    graph,
    ranker,
    traffic_predictor,
    preferences,
) -> list[dict]:
    """
    Score and sort candidate routes using the AI ranker.
    Enriches each route with highlights and a composite score.
    """
    scored = []
    for i, route in enumerate(candidates):
        # Weights from preferences
        time_w    = getattr(preferences, "time_weight", 0.4)
        quality_w = getattr(preferences, "road_quality_weight", 0.3)
        driver_w  = getattr(preferences, "driver_score_weight", 0.3)

        # Normalise ETA (lower is better → invert)
        eta_score = max(0, 1 - route["eta_minutes"] / 120)

        composite = (
            eta_score                    * time_w +
            route["road_quality_score"]  * quality_w +
            route["driver_score"]        * driver_w
        )

        # Optionally use ML ranker if model loaded
        try:
            features = _extract_features(route)
            ml_score = ranker.score(features)
            composite = 0.5 * composite + 0.5 * ml_score
        except Exception:
            pass

        route["composite_score"] = round(composite, 4)
        scored.append(route)

    scored.sort(key=lambda r: r["composite_score"], reverse=True)

    # Add highlights
    for i, route in enumerate(scored[:3]):
        route["highlights"] = LABEL_HIGHLIGHTS.get(i, [])

    return scored


def _extract_features(route: dict) -> list[float]:
    return [
        route["distance_km"],
        route["eta_minutes"],
        route["road_quality_score"],
        route["driver_score"],
        route["safety_score"],
    ]
