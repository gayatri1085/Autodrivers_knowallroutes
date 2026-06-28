"""
Road Quality Scorer

Computes a composite road quality score (0–1) from:
- OSM tags (surface, smoothness, lanes, width)
- Accident history
- Flood risk zone

Higher score = better road quality.
"""

from typing import Optional


# OSM surface tag → quality score
SURFACE_SCORES = {
    "asphalt":        0.95,
    "concrete":       0.90,
    "paved":          0.85,
    "compacted":      0.65,
    "fine_gravel":    0.60,
    "gravel":         0.45,
    "unpaved":        0.35,
    "dirt":           0.20,
    "mud":            0.10,
}

SMOOTHNESS_SCORES = {
    "excellent":      1.00,
    "good":           0.85,
    "intermediate":   0.65,
    "bad":            0.40,
    "very_bad":       0.20,
    "horrible":       0.05,
    "impassable":     0.00,
}

HIGHWAY_BASE_SCORES = {
    "motorway":       0.90,
    "trunk":          0.85,
    "primary":        0.80,
    "secondary":      0.70,
    "tertiary":       0.60,
    "unclassified":   0.50,
    "residential":    0.50,
    "service":        0.40,
    "track":          0.25,
    "path":           0.15,
}


def compute_road_score(
    way_id: Optional[int],
    osm_tags: Optional[dict] = None,
    accident_count: int = 0,
    is_flood_zone: bool = False,
) -> float:
    """
    Compute road quality score for a given OSM way.

    Args:
        way_id: OSM way ID (used to fetch tags from DB if osm_tags not provided)
        osm_tags: Pre-fetched OSM tags dict
        accident_count: Number of accidents on this segment in past 12 months
        is_flood_zone: Whether the road is in a known flood zone

    Returns:
        float: 0.0 (worst) to 1.0 (best)
    """
    if osm_tags is None:
        osm_tags = _fetch_tags_from_db(way_id) or {}

    # Base score from highway type
    highway = osm_tags.get("highway", "unclassified")
    base = HIGHWAY_BASE_SCORES.get(highway, 0.50)

    # Surface modifier
    surface = osm_tags.get("surface", "")
    surface_score = SURFACE_SCORES.get(surface, base)

    # Smoothness modifier
    smoothness = osm_tags.get("smoothness", "")
    smoothness_score = SMOOTHNESS_SCORES.get(smoothness, surface_score)

    # Width modifier (wider = better for Indian traffic)
    try:
        width = float(str(osm_tags.get("width", "4")).split()[0])
        width_bonus = min(0.1, (width - 4) * 0.02)
    except (ValueError, TypeError):
        width_bonus = 0.0

    # Combine
    score = (smoothness_score * 0.5 + surface_score * 0.3 + base * 0.2) + width_bonus

    # Penalties
    accident_penalty = min(0.3, accident_count * 0.05)
    flood_penalty    = 0.2 if is_flood_zone else 0.0

    score = max(0.0, min(1.0, score - accident_penalty - flood_penalty))
    return round(score, 3)


def _fetch_tags_from_db(way_id: Optional[int]) -> Optional[dict]:
    """Fetch OSM tags from PostGIS database. Returns None if not found."""
    if way_id is None:
        return None
    # TODO: implement DB lookup with asyncpg
    return None
