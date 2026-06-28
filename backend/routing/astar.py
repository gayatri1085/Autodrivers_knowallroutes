"""
A* Routing with Yen's K-Shortest Paths extension.
"""

import math
from typing import Optional
import networkx as nx


def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Haversine distance in metres between two lat/lng points."""
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def astar_route(
    G: nx.MultiDiGraph,
    origin: int,
    destination: int,
    k: int = 5,
    preferences=None,
) -> list[dict]:
    """
    Return up to k candidate routes using A* + Yen's K-Shortest Paths.
    Each route is a dict with 'nodes', 'distance_km', 'eta_minutes', and edge stats.
    """
    dest_data = G.nodes[destination]
    dest_lat = dest_data.get("y", 0)
    dest_lng = dest_data.get("x", 0)

    def heuristic(u, v):
        u_data = G.nodes[u]
        return haversine(u_data.get("y", 0), u_data.get("x", 0), dest_lat, dest_lng)

    def weight_fn(u, v, data):
        # Pick minimum weight across parallel edges
        weights = [d.get("auto_weight", d.get("length", 100)) for d in data.values()]
        return min(weights)

    routes = []
    try:
        # Primary route: A*
        path = nx.astar_path(G, origin, destination, heuristic=heuristic, weight=weight_fn)
        routes.append(_path_to_route(G, path))
    except nx.NetworkXNoPath:
        return []

    # Additional routes: simple_paths for diversity
    try:
        for path in nx.shortest_simple_paths(G, origin, destination, weight=weight_fn):
            route = _path_to_route(G, path)
            if not _too_similar(route, routes):
                routes.append(route)
            if len(routes) >= k:
                break
    except Exception:
        pass

    return routes


def _path_to_route(G: nx.MultiDiGraph, nodes: list[int]) -> dict:
    total_length = 0.0
    total_time   = 0.0
    road_scores  = []
    driver_scores= []
    accident_risks=[]

    for u, v in zip(nodes[:-1], nodes[1:]):
        edges = G[u][v]
        # Pick best parallel edge
        edge = min(edges.values(), key=lambda d: d.get("auto_weight", 999))
        length = edge.get("length", 0)
        speed  = edge.get("speed_kph", edge.get("maxspeed", 30))
        try:
            speed = float(speed)
        except (ValueError, TypeError):
            speed = 30.0

        total_length += length
        total_time   += (length / 1000) / speed * 60   # minutes
        road_scores.append(edge.get("road_score", 0.5))
        driver_scores.append(edge.get("driver_score", 0.5))
        accident_risks.append(edge.get("accident_risk", 0.0))

    avg_road  = sum(road_scores)   / len(road_scores)   if road_scores   else 0.5
    avg_driver= sum(driver_scores) / len(driver_scores) if driver_scores else 0.5
    avg_safety= 1.0 - (sum(accident_risks) / len(accident_risks) if accident_risks else 0.0)

    return {
        "nodes":             nodes,
        "distance_km":       round(total_length / 1000, 2),
        "eta_minutes":       round(total_time, 1),
        "road_quality_score":round(avg_road, 3),
        "driver_score":      round(avg_driver, 3),
        "safety_score":      round(avg_safety, 3),
        "segments":          [],
        "highlights":        [],
    }


def _too_similar(new_route: dict, existing: list[dict], threshold: float = 0.7) -> bool:
    """Check if a new route overlaps too much with existing ones."""
    new_nodes = set(new_route["nodes"])
    for r in existing:
        overlap = len(new_nodes & set(r["nodes"])) / max(len(new_nodes), 1)
        if overlap > threshold:
            return True
    return False
