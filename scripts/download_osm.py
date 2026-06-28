"""
Download OSM data for a city via Overpass API.

Usage:
    python scripts/download_osm.py --city chennai
"""

import argparse
import json
import sys
from pathlib import Path

import httpx

DATA_DIR = Path(__file__).parent.parent / "data" / "osm"

CITY_QUERIES = {
    "chennai":   '["Chennai","IN-TN"]',
    "bengaluru": '["Bengaluru","IN-KA"]',
    "hyderabad": '["Hyderabad","IN-TG"]',
    "kochi":     '["Kochi","IN-KL"]',
}

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def download_osm(city: str):
    if city not in CITY_QUERIES:
        print(f"Unknown city: {city}")
        sys.exit(1)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_DIR / f"{city}.geojson"

    # Simplified query: roads and amenities
    query = f"""
    [out:json][timeout:120];
    area["name"~"{city}", i]["admin_level"~"6|7|8"]->.searchArea;
    (
      way["highway"](area.searchArea);
    );
    out body geom;
    """

    print(f"Downloading OSM data for {city}...")
    try:
        resp = httpx.post(OVERPASS_URL, data={"data": query}, timeout=180)
        resp.raise_for_status()
        data = resp.json()
        with open(out_path, "w") as f:
            json.dump(data, f)
        print(f"✅ Saved {len(data.get('elements', []))} elements to {out_path}")
    except Exception as e:
        print(f"❌ Download failed: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", required=True)
    args = parser.parse_args()
    download_osm(args.city)
