"""
Route Ranker — LightGBM model that scores candidate routes.
"""

from pathlib import Path
import numpy as np

MODELS_DIR = Path(__file__).parent.parent.parent / "models"

FEATURE_NAMES = [
    "distance_km",
    "eta_minutes",
    "road_quality_score",
    "driver_score",
    "safety_score",
]


class RouteRanker:
    def __init__(self):
        self._model = None
        self._load()

    def _load(self):
        model_path = MODELS_DIR / "route_ranker.pkl"
        if not model_path.exists():
            return
        try:
            import joblib
            self._model = joblib.load(model_path)
            print("[RouteRanker] Model loaded.")
        except Exception as e:
            print(f"[RouteRanker] Could not load model: {e}")

    def score(self, features: list[float]) -> float:
        """Return predicted driver preference score 0–1."""
        if self._model is None:
            return 0.5
        X = np.array(features).reshape(1, -1)
        return float(self._model.predict(X)[0])

    def score_batch(self, features_list: list[list[float]]) -> list[float]:
        if self._model is None:
            return [0.5] * len(features_list)
        X = np.array(features_list)
        return self._model.predict(X).tolist()
