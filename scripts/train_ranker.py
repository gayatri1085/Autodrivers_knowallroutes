"""
Train the route ranking model.

Usage:
    python scripts/train_ranker.py --data data/traffic/
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path
import joblib
from lightgbm import LGBMRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

MODELS_DIR = Path(__file__).parent.parent / "models"
FEATURE_COLS = ["distance_km", "eta_minutes", "road_quality_score", "driver_score", "safety_score"]
TARGET_COL   = "user_rating"


def train(data_dir: str):
    data_path = Path(data_dir)
    csvs = list(data_path.glob("*.csv"))
    if not csvs:
        print("No CSV files found in data/traffic/. Provide route feedback CSVs.")
        return

    df = pd.concat([pd.read_csv(f) for f in csvs], ignore_index=True)
    df = df.dropna(subset=FEATURE_COLS + [TARGET_COL])

    X = df[FEATURE_COLS].values
    y = df[TARGET_COL].values / 5.0   # Normalise 1-5 rating to 0-1

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LGBMRegressor(n_estimators=200, learning_rate=0.05, num_leaves=31, random_state=42)
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)])

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    print(f"Test MAE: {mae:.4f}")

    MODELS_DIR.mkdir(exist_ok=True)
    out_path = MODELS_DIR / "route_ranker.pkl"
    joblib.dump(model, out_path)
    print(f"✅ Saved to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/traffic/")
    args = parser.parse_args()
    train(args.data)
