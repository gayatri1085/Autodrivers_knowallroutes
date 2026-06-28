"""
Traffic Predictor — time-of-day and location-aware congestion forecast.
"""

from datetime import datetime
from pathlib import Path
import math

MODELS_DIR = Path(__file__).parent.parent.parent / "models"

# Rough peak hours for South Indian cities
PEAK_HOURS = {
    "morning": (7, 10),    # 7–10 AM
    "evening": (17, 20),   # 5–8 PM
    "school":  (12, 14),   # School dismissal
}

CONGESTION_DESCRIPTIONS = {
    (0.0, 0.3): ("Low", "Roads are clear. Good time to travel."),
    (0.3, 0.6): ("Moderate", "Some traffic. Allow 10–15 min extra."),
    (0.6, 0.8): ("High", "Heavy traffic. Consider an alternate route."),
    (0.8, 1.1): ("Severe", "Gridlock likely. Strongly consider alternate timing."),
}


class TrafficPredictor:
    def __init__(self):
        self._model = None
        self._load()

    def _load(self):
        model_path = MODELS_DIR / "traffic_model.pkl"
        if not model_path.exists():
            return
        try:
            import joblib
            self._model = joblib.load(model_path)
        except Exception as e:
            print(f"[TrafficPredictor] Could not load model: {e}")

    def predict(self, lat: float, lng: float, city: str, horizon_minutes: int = 30) -> dict:
        """Predict congestion level (0–1) at a location and time."""
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()

        if self._model:
            features = self._build_features(lat, lng, hour, weekday)
            level = float(self._model.predict([features])[0])
        else:
            level = self._rule_based(hour, weekday)

        # Project into future (crude linear decay)
        if horizon_minutes > 30:
            level *= max(0.6, 1 - (horizon_minutes - 30) / 200)

        label, description = self._describe(level)
        recommended = self._recommend_departure(level, now)

        return {
            "level": round(min(1.0, max(0.0, level)), 3),
            "label": label,
            "description": description,
            "recommended_departure": recommended,
        }

    def _rule_based(self, hour: int, weekday: int) -> float:
        is_weekday = weekday < 5
        if is_weekday:
            if PEAK_HOURS["morning"][0] <= hour < PEAK_HOURS["morning"][1]:
                return 0.85
            if PEAK_HOURS["evening"][0] <= hour < PEAK_HOURS["evening"][1]:
                return 0.90
            if PEAK_HOURS["school"][0] <= hour < PEAK_HOURS["school"][1]:
                return 0.65
            if 22 <= hour or hour < 6:
                return 0.15
            return 0.45
        else:
            if 11 <= hour < 20:
                return 0.50
            return 0.20

    def _build_features(self, lat, lng, hour, weekday):
        return [lat, lng, hour, weekday, math.sin(2 * math.pi * hour / 24), math.cos(2 * math.pi * hour / 24)]

    def _describe(self, level: float) -> tuple[str, str]:
        for (lo, hi), (label, desc) in CONGESTION_DESCRIPTIONS.items():
            if lo <= level < hi:
                return label, desc
        return "Unknown", ""

    def _recommend_departure(self, level: float, now: datetime) -> str | None:
        if level < 0.6:
            return None
        # Suggest leaving after peak
        hour = now.hour
        if PEAK_HOURS["morning"][0] <= hour < PEAK_HOURS["morning"][1]:
            return f"After {PEAK_HOURS['morning'][1]}:00 AM"
        if PEAK_HOURS["evening"][0] <= hour < PEAK_HOURS["evening"][1]:
            return f"After {PEAK_HOURS['evening'][1]}:00 PM"
        return None
