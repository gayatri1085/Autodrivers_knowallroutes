"""
Build the road network graph for a given city.

Usage:
    python scripts/build_graph.py --city chennai
    python scripts/build_graph.py --city bengaluru
    python scripts/build_graph.py --all
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from routing.graph_builder import build_graph

SUPPORTED_CITIES = ["chennai", "bengaluru", "hyderabad", "kochi"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build road graph for AutoRouteAI")
    parser.add_argument("--city", type=str, help="City to build graph for")
    parser.add_argument("--all", action="store_true", help="Build graphs for all supported cities")
    args = parser.parse_args()

    cities = SUPPORTED_CITIES if args.all else ([args.city] if args.city else [])
    if not cities:
        parser.error("Provide --city CITY or --all")

    for city in cities:
        if city not in SUPPORTED_CITIES:
            print(f"⚠️  '{city}' not in supported cities: {SUPPORTED_CITIES}")
            continue
        print(f"\n🚖 Building graph for {city}...")
        try:
            G = build_graph(city)
            print(f"✅ {city}: {len(G.nodes)} nodes, {len(G.edges)} edges")
        except Exception as e:
            print(f"❌ Failed for {city}: {e}")
