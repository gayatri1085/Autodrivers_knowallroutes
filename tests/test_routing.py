"""
Tests for routing algorithms and road scoring.
"""

import pytest
import networkx as nx
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from routing.astar import astar_route, haversine, _path_to_route
from routing.dijkstra import dijkstra_route
from routing.road_score import compute_road_score


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def simple_graph():
    """A tiny road graph for testing."""
    G = nx.MultiDiGraph()
    # 4 nodes in a rough Chennai grid
    G.add_node(1, y=13.00, x=80.20)
    G.add_node(2, y=13.01, x=80.20)
    G.add_node(3, y=13.01, x=80.21)
    G.add_node(4, y=13.00, x=80.21)

    edges = [
        (1, 2, {"length": 1000, "speed_kph": 40, "road_score": 0.8, "driver_score": 0.75, "accident_risk": 0.1, "auto_weight": 10}),
        (2, 3, {"length": 800,  "speed_kph": 30, "road_score": 0.6, "driver_score": 0.60, "accident_risk": 0.2, "auto_weight": 15}),
        (3, 4, {"length": 1000, "speed_kph": 40, "road_score": 0.9, "driver_score": 0.90, "accident_risk": 0.0, "auto_weight": 8}),
        (1, 4, {"length": 1500, "speed_kph": 50, "road_score": 0.5, "driver_score": 0.50, "accident_risk": 0.3, "auto_weight": 20}),
    ]
    for u, v, data in edges:
        G.add_edge(u, v, **data)
    return G


# ── Haversine ─────────────────────────────────────────────────────────────────

def test_haversine_same_point():
    assert haversine(13.0, 80.2, 13.0, 80.2) == pytest.approx(0.0, abs=1e-6)


def test_haversine_known_distance():
    # Approx 1 degree lat ≈ 111 km
    dist = haversine(0.0, 0.0, 1.0, 0.0)
    assert 110_000 < dist < 112_000


# ── A* Routing ────────────────────────────────────────────────────────────────

def test_astar_finds_path(simple_graph):
    routes = astar_route(simple_graph, 1, 4, k=3)
    assert len(routes) >= 1
    assert routes[0]["nodes"][0] == 1
    assert routes[0]["nodes"][-1] == 4


def test_astar_returns_dict_keys(simple_graph):
    routes = astar_route(simple_graph, 1, 3, k=1)
    assert len(routes) >= 1
    required = {"nodes", "distance_km", "eta_minutes", "road_quality_score", "driver_score", "safety_score"}
    assert required.issubset(routes[0].keys())


def test_astar_no_path():
    G = nx.MultiDiGraph()
    G.add_node(1, y=13.0, x=80.0)
    G.add_node(2, y=13.1, x=80.0)
    # No edges
    routes = astar_route(G, 1, 2)
    assert routes == []


def test_path_to_route_distance(simple_graph):
    route = _path_to_route(simple_graph, [1, 2, 3])
    # 1000 + 800 = 1800m = 1.8km
    assert route["distance_km"] == pytest.approx(1.8, abs=0.01)


# ── Dijkstra ─────────────────────────────────────────────────────────────────

def test_dijkstra_finds_shortest(simple_graph):
    result = dijkstra_route(simple_graph, 1, 4, weight="length")
    assert result is not None
    assert result["nodes"][0] == 1
    assert result["nodes"][-1] == 4


def test_dijkstra_no_path():
    G = nx.MultiDiGraph()
    G.add_node(1, y=0, x=0)
    G.add_node(2, y=1, x=1)
    result = dijkstra_route(G, 1, 2)
    assert result is None


# ── Road Score ────────────────────────────────────────────────────────────────

def test_road_score_asphalt_excellent():
    score = compute_road_score(None, {"highway": "primary", "surface": "asphalt", "smoothness": "excellent"})
    assert score > 0.85


def test_road_score_dirt_road():
    score = compute_road_score(None, {"highway": "track", "surface": "dirt"})
    assert score < 0.35


def test_road_score_flood_penalty():
    score_no_flood = compute_road_score(None, {"highway": "secondary"}, is_flood_zone=False)
    score_flood    = compute_road_score(None, {"highway": "secondary"}, is_flood_zone=True)
    assert score_flood < score_no_flood


def test_road_score_accident_penalty():
    score_safe    = compute_road_score(None, {"highway": "primary"}, accident_count=0)
    score_unsafe  = compute_road_score(None, {"highway": "primary"}, accident_count=6)
    assert score_unsafe < score_safe


def test_road_score_range():
    for surface in ["asphalt", "concrete", "gravel", "dirt", "mud"]:
        score = compute_road_score(None, {"surface": surface})
        assert 0.0 <= score <= 1.0
