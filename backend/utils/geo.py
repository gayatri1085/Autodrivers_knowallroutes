"""
Geo utilities — coordinate snapping, geometry extraction, GeoJSON helpers.
"""

import math
from typing import Optional
import networkx as nx


def coords_to_node(G: nx.MultiDiGraph, lat: float, lng: float) -> Optional[int]:
    """
    Snap a lat/lng coordinate to the nearest graph node.
    Returns the node ID or None if graph is empty.
    """
    if G is None or len(G.nodes) == 0:
        return None

    best_node = None
    best_dist = float("inf")

    for node, data in G.nodes(data=True):
        node_lat = data.get("y", 0)
        node_lng = data.get("x", 0)
        dist = haversine(lat, lng, node_lat, node_lng)
        if dist < best_dist:
            best_dist = dist
            best_node = node

    return best_node


def route_geometry(G: nx.MultiDiGraph, nodes: list[int]) -> list[list[float]]:
    """
    Extract [lng, lat] coordinate pairs for a sequence of nodes.
    MapLibre / GeoJSON uses [lng, lat] order.
    """
    coords = []
    for node in nodes:
        data = G.nodes[node]
        lat = data.get("y", 0)
        lng = data.get("x", 0)
        coords.append([lng, lat])
    return coords


def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Haversine distance in metres."""
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def bbox_from_center(lat: float, lng: float, radius_m: float = 5000) -> dict:
    """Return a bounding box dict around a center point."""
    delta_lat = radius_m / 111_320
    delta_lng = radius_m / (111_320 * math.cos(math.radians(lat)))
    return {
        "min_lat": lat - delta_lat,
        "max_lat": lat + delta_lat,
        "min_lng": lng - delta_lng,
        "max_lng": lng + delta_lng,
    }


def geojson_linestring(coords: list[list[float]]) -> dict:
    return {
        "type": "Feature",
        "geometry": {"type": "LineString", "coordinates": coords},
        "properties": {},
    }
