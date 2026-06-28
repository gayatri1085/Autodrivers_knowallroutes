"""
Dijkstra's shortest path — used for baseline comparison and fallback.
"""

import networkx as nx


def dijkstra_route(G: nx.MultiDiGraph, origin: int, destination: int, weight: str = "length") -> dict | None:
    """
    Find the shortest path by a given weight (length, travel_time, auto_weight).
    Returns a route dict or None if no path exists.
    """
    try:
        length, path = nx.single_source_dijkstra(G, origin, destination, weight=weight)
    except nx.NetworkXNoPath:
        return None

    total_length = sum(
        min(G[u][v][k].get("length", 0) for k in G[u][v])
        for u, v in zip(path[:-1], path[1:])
    )

    return {
        "nodes": path,
        "distance_km": round(total_length / 1000, 2),
        "eta_minutes": round(length / 8 / 60, 1) if weight == "length" else round(length, 1),
        "road_quality_score": 0.5,
        "driver_score": 0.5,
        "safety_score": 0.5,
        "segments": [],
        "highlights": ["Shortest path by distance"],
    }
