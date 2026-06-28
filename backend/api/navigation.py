"""
Navigation API — /route, /search, /road_score, /feedback endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional

from routing.graph_builder import get_graph
from routing.astar import astar_route
from routing.reranker import rerank_routes
from ai.route_ranker import RouteRanker
from ai.traffic_predictor import TrafficPredictor
from utils.geo import coords_to_node, route_geometry

router = APIRouter()

ranker = RouteRanker()
traffic_predictor = TrafficPredictor()


# ── Schemas ───────────────────────────────────────────────────────────────────

class LatLng(BaseModel):
    lat: float
    lng: float


class RoutePreferences(BaseModel):
    avoid_floods: bool = True
    road_quality_weight: float = Field(0.3, ge=0, le=1)
    time_weight: float = Field(0.4, ge=0, le=1)
    driver_score_weight: float = Field(0.3, ge=0, le=1)


class RouteRequest(BaseModel):
    origin: LatLng
    destination: LatLng
    city: str = "chennai"
    preferences: RoutePreferences = RoutePreferences()


class RouteSegment(BaseModel):
    coordinates: list[list[float]]
    road_name: str
    road_quality: float
    driver_sentiment: float


class RouteResult(BaseModel):
    route_id: str
    label: str                   # "Driver Recommended" | "Fastest" | "Alternative"
    eta_minutes: float
    distance_km: float
    road_quality_score: float
    safety_score: float
    driver_score: float
    geometry: list[list[float]]  # GeoJSON LineString coordinates
    segments: list[RouteSegment]
    highlights: list[str]        # Human-readable reasons to pick this route


class RouteResponse(BaseModel):
    routes: list[RouteResult]
    city: str
    origin: LatLng
    destination: LatLng


class FeedbackRequest(BaseModel):
    route_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    city: str = "chennai"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/route", response_model=RouteResponse)
async def get_route(req: RouteRequest):
    """
    Generate AI-ranked routes between two points.

    Returns up to 3 routes ordered by AutoRouteAI's composite score:
    time + road quality + driver sentiment + safety.
    """
    city = req.city.lower()
    graph = get_graph(city)
    if graph is None:
        raise HTTPException(status_code=404, detail=f"City '{city}' not found. Run scripts/build_graph.py first.")

    origin_node = coords_to_node(graph, req.origin.lat, req.origin.lng)
    dest_node   = coords_to_node(graph, req.destination.lat, req.destination.lng)

    if origin_node is None or dest_node is None:
        raise HTTPException(status_code=422, detail="Could not snap coordinates to road network.")

    # Generate K candidate routes
    candidates = astar_route(graph, origin_node, dest_node, k=5, preferences=req.preferences)

    if not candidates:
        raise HTTPException(status_code=404, detail="No route found between the given points.")

    # AI re-ranking
    ranked = await rerank_routes(candidates, graph, ranker, traffic_predictor, req.preferences)

    routes = []
    labels = ["Driver Recommended", "Fastest", "Alternative"]
    for i, route in enumerate(ranked[:3]):
        geom = route_geometry(graph, route["nodes"])
        routes.append(RouteResult(
            route_id=f"route_{i}_{hash(str(route['nodes']))}",
            label=labels[i] if i < len(labels) else f"Option {i+1}",
            eta_minutes=route["eta_minutes"],
            distance_km=route["distance_km"],
            road_quality_score=route["road_quality_score"],
            safety_score=route["safety_score"],
            driver_score=route["driver_score"],
            geometry=geom,
            segments=route.get("segments", []),
            highlights=route.get("highlights", []),
        ))

    return RouteResponse(
        routes=routes,
        city=city,
        origin=req.origin,
        destination=req.destination,
    )


@router.get("/search")
async def search_location(
    q: str = Query(..., min_length=2),
    city: str = Query("chennai"),
):
    """
    Geocode a place name within the specified city using Nominatim.
    Returns a list of candidate locations with coordinates.
    """
    import httpx

    city_country = f"{q}, {city}, India"
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city_country, "format": "json", "limit": 5},
            headers={"User-Agent": "AutoRouteAI/1.0"},
        )
    results = resp.json()
    return [
        {
            "display_name": r["display_name"],
            "lat": float(r["lat"]),
            "lng": float(r["lon"]),
            "type": r.get("type", ""),
        }
        for r in results
    ]


@router.get("/road_score")
async def road_score(way_id: int):
    """
    Return the composite road quality score for an OSM way ID.
    """
    from routing.road_score import compute_road_score
    score = compute_road_score(way_id)
    if score is None:
        raise HTTPException(status_code=404, detail=f"Way {way_id} not in database.")
    return {"way_id": way_id, "road_score": score}


@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Accept driver/rider feedback to improve the route ranking model.
    Feedback is stored and used in periodic retraining.
    """
    # TODO: persist to DB and queue for retraining
    return {"status": "accepted", "route_id": feedback.route_id}
