"""
Graph Builder — loads OSM road network into a NetworkX graph with enriched edge weights.
"""

import os
import pickle
from pathlib import Path
from typing import Optional

import networkx as nx
import osmnx as ox

from routing.road_score import compute_road_score

_GRAPH_CACHE: dict[str, nx.MultiDiGraph] = {}
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "osm"


def get_graph(city: str) -> Optional[nx.MultiDiGraph]:
    """Return cached graph for a city, loading from disk if needed."""
    if city in _GRAPH_CACHE:
        return _GRAPH_CACHE[city]

    graph_path = DATA_DIR / f"{city}_graph.pkl"
    if graph_path.exists():
        with open(graph_path, "rb") as f:
            G = pickle.load(f)
        _GRAPH_CACHE[city] = G
        return G

    return None   # Not built yet — run scripts/build_graph.py


def build_graph(city: str, save: bool = True) -> nx.MultiDiGraph:
    """
    Download OSM road network for a city and enrich edges with route-scoring weights.
    Saves to disk for fast loading later.
    """
    city_query = f"{city.title()}, India"
    print(f"Downloading OSM network for {city_query}...")
    G = ox.graph_from_place(city_query, network_type="drive", simplify=True)

    print("Enriching edges with road scores...")
    for u, v, k, data in G.edges(data=True, keys=True):
        way_id = data.get("osmid")
        score = compute_road_score(way_id) if way_id else 0.5
        data["road_score"]   = score
        data["driver_score"] = score      # Will be updated with sentiment model
        data["flood_risk"]   = 0.0        # Updated by weather layer
        data["accident_risk"]= 0.0        # Updated from accident data
        # Composite weight for routing: lower = more preferred
        data["auto_weight"]  = _composite_weight(data)

    if save:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(DATA_DIR / f"{city}_graph.pkl", "wb") as f:
            pickle.dump(G, f)
        print(f"Saved graph for {city}.")

    _GRAPH_CACHE[city] = G
    return G


def _composite_weight(edge_data: dict) -> float:
    """
    Lower is better. Combines travel time, road quality, and safety.
    """
    travel_time  = edge_data.get("travel_time", edge_data.get("length", 100) / 8)
    road_score   = edge_data.get("road_score", 0.5)
    flood_risk   = edge_data.get("flood_risk", 0.0)
    accident_risk= edge_data.get("accident_risk", 0.0)

    quality_penalty = (1.0 - road_score) * 30    # bad road → higher cost
    flood_penalty   = flood_risk * 100
    accident_penalty= accident_risk * 50

    return travel_time + quality_penalty + flood_penalty + accident_penalty
