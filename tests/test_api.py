"""
Integration tests for FastAPI endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app import app


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_graph():
    """Mock graph so tests don't need OSM data on disk."""
    import networkx as nx
    G = nx.MultiDiGraph()
    G.add_node(1, y=13.0827, x=80.2707)
    G.add_node(2, y=13.0604, x=80.2496)
    G.add_edge(1, 2,
        length=3500, speed_kph=40,
        road_score=0.75, driver_score=0.70,
        accident_risk=0.1, flood_risk=0.0,
        auto_weight=12,
    )
    return G


@pytest.fixture
def mock_route_response():
    return {
        "routes": [
            {
                "route_id": "route_0_abc123",
                "label": "Driver Recommended",
                "eta_minutes": 12.5,
                "distance_km": 3.5,
                "road_quality_score": 0.75,
                "safety_score": 0.80,
                "driver_score": 0.70,
                "geometry": [[80.2707, 13.0827], [80.2600, 13.0700], [80.2496, 13.0604]],
                "segments": [],
                "highlights": ["Preferred by local auto drivers", "Smoother road surface"],
            }
        ],
        "city": "chennai",
        "origin": {"lat": 13.0827, "lng": 80.2707},
        "destination": {"lat": 13.0604, "lng": 80.2496},
    }


# ── Health ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# ── /api/route ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_route_missing_city():
    """Should return 404 if city graph not built."""
    payload = {
        "origin": {"lat": 13.0827, "lng": 80.2707},
        "destination": {"lat": 13.0604, "lng": 80.2496},
        "city": "atlantis",
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/route", json=payload)
    assert resp.status_code == 404
    assert "atlantis" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_route_returns_structure(mock_graph, mock_route_response):
    """Mock the graph and routing pipeline; verify response schema."""
    with patch("api.navigation.get_graph", return_value=mock_graph), \
         patch("api.navigation.coords_to_node", side_effect=[1, 2]), \
         patch("api.navigation.astar_route", return_value=[
             {
                 "nodes": [1, 2],
                 "distance_km": 3.5,
                 "eta_minutes": 12.5,
                 "road_quality_score": 0.75,
                 "driver_score": 0.70,
                 "safety_score": 0.80,
                 "segments": [],
                 "highlights": [],
             }
         ]), \
         patch("api.navigation.rerank_routes", new_callable=AsyncMock, return_value=[
             {
                 "nodes": [1, 2],
                 "distance_km": 3.5,
                 "eta_minutes": 12.5,
                 "road_quality_score": 0.75,
                 "driver_score": 0.70,
                 "safety_score": 0.80,
                 "segments": [],
                 "highlights": ["Preferred by local auto drivers"],
                 "composite_score": 0.73,
             }
         ]), \
         patch("api.navigation.route_geometry", return_value=[[80.27, 13.08], [80.25, 13.06]]):

        payload = {
            "origin": {"lat": 13.0827, "lng": 80.2707},
            "destination": {"lat": 13.0604, "lng": 80.2496},
            "city": "chennai",
        }
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/route", json=payload)

    assert resp.status_code == 200
    data = resp.json()
    assert "routes" in data
    assert len(data["routes"]) >= 1
    route = data["routes"][0]
    for key in ("route_id", "label", "eta_minutes", "distance_km", "geometry"):
        assert key in route, f"Missing key: {key}"


# ── /api/search ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_search_returns_list():
    mock_nominatim = [
        {
            "display_name": "T. Nagar, Chennai, Tamil Nadu, India",
            "lat": "13.0418",
            "lon": "80.2341",
            "type": "suburb",
        }
    ]
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_resp = MagicMock()
        mock_resp.json.return_value = mock_nominatim
        mock_get.return_value = mock_resp

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/search?q=T+Nagar&city=chennai")

    assert resp.status_code == 200
    results = resp.json()
    assert isinstance(results, list)


@pytest.mark.asyncio
async def test_search_query_too_short():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/search?q=T")
    assert resp.status_code == 422   # Pydantic min_length=2 → 1 char fails


# ── /api/traffic ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_traffic_returns_level():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/traffic?lat=13.0827&lng=80.2707&city=chennai")
    assert resp.status_code == 200
    data = resp.json()
    assert "congestion_level" in data
    assert 0.0 <= data["congestion_level"] <= 1.0


@pytest.mark.asyncio
async def test_traffic_invalid_horizon():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/traffic?lat=13.0&lng=80.2&city=chennai&horizon_minutes=999")
    assert resp.status_code == 422


# ── /api/feedback ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_feedback_accepted():
    payload = {
        "route_id": "route_0_abc123",
        "rating": 4,
        "comment": "Good road, no potholes",
        "city": "chennai",
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/feedback", json=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "accepted"


@pytest.mark.asyncio
async def test_feedback_invalid_rating():
    payload = {"route_id": "abc", "rating": 10, "city": "chennai"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/feedback", json=payload)
    assert resp.status_code == 422
