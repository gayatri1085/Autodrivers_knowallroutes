"""
Train the road sentiment classifier.

Usage:
    python scripts/train_sentiment.py --data data/sentiment/
"""

import argparse
import json
from pathlib import Path
import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


MODELS_DIR = Path(__file__).parent.parent / "models"


def load_data(data_dir: Path) -> tuple[list, list]:
    texts, labels = [], []
    for split in ["train.jsonl", "val.jsonl"]:
        path = data_dir / split
        if path.exists():
            with open(path) as f:
                for line in f:
                    item = json.loads(line)
                    texts.append(item["text"])
                    labels.append(item["label"])
    return texts, labels


def train(data_dir: str):
    data_path = Path(data_dir)
    texts, labels = load_data(data_path)

    if len(texts) == 0:
        print("No training data found. Create data/sentiment/train.jsonl with {text, label} per line.")
        return

    print(f"Training on {len(texts)} examples...")
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=20_000)),
        ("clf",   LogisticRegression(max_iter=500, C=1.0)),
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred))

    MODELS_DIR.mkdir(exist_ok=True)
    out_path = MODELS_DIR / "sentiment_classifier.pkl"
    joblib.dump(pipeline, out_path)
    print(f"✅ Saved to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/sentiment/")
    args = parser.parse_args()
    train(args.data)
