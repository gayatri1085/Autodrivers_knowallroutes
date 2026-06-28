"""
AutoRouteAI Configuration
Copy this file to config.py and fill in your API keys.
config.py is git-ignored.
"""

import os
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / ".." / "data"
MODELS_DIR = BASE_DIR / ".." / "models"

# ── Database ──────────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://autorouteai:autorouteai_secret@localhost:5432/autorouteai"
)

# ── Redis ─────────────────────────────────────────────────────────────────────
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# ── API Keys (replace with your own) ─────────────────────────────────────────
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "your_key_here")
ORS_API_KEY = os.getenv("ORS_API_KEY", "your_key_here")       # OpenRouteService

# ── Routing ───────────────────────────────────────────────────────────────────
DEFAULT_CITY = os.getenv("CITY_DEFAULT", "chennai")
K_ROUTES = 5          # Number of candidate routes before re-ranking
TOP_ROUTES = 3        # Routes returned to client

CITY_BOUNDS = {
    "chennai":   {"lat": (12.85, 13.25), "lng": (80.15, 80.35)},
    "bengaluru": {"lat": (12.80, 13.15), "lng": (77.45, 77.80)},
    "hyderabad": {"lat": (17.25, 17.60), "lng": (78.30, 78.65)},
    "kochi":     {"lat": (9.85,  10.10), "lng": (76.20, 76.40)},
}

# ── AI / ML ───────────────────────────────────────────────────────────────────
SENTIMENT_MODEL_NAME = "roberta-base"
SENTIMENT_MODEL_PATH = MODELS_DIR / "sentiment_classifier.pkl"
ROUTE_RANKER_PATH    = MODELS_DIR / "route_ranker.pkl"
TRAFFIC_MODEL_PATH   = MODELS_DIR / "traffic_model.pkl"

DEVICE = "cpu"   # Set to "cuda" if GPU is available

# ── Route Scoring Weights ─────────────────────────────────────────────────────
WEIGHT_TIME           = 0.35
WEIGHT_ROAD_QUALITY   = 0.30
WEIGHT_DRIVER_SCORE   = 0.20
WEIGHT_SAFETY         = 0.15

# ── Cache ─────────────────────────────────────────────────────────────────────
ROUTE_CACHE_TTL = 300   # seconds
TRAFFIC_CACHE_TTL = 60
