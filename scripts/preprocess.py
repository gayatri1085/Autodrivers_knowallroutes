"""
Preprocess raw data into formats expected by AutoRouteAI.

Usage:
    python scripts/preprocess.py --type sentiment
    python scripts/preprocess.py --type accidents
"""

import argparse
import json
import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def preprocess_sentiment():
    """
    Convert raw scraped feedback into JSONL training format.
    Input: data/sentiment/raw/*.json
    Output: data/sentiment/train.jsonl
    """
    raw_dir = DATA_DIR / "sentiment" / "raw"
    out_path = DATA_DIR / "sentiment" / "train.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with open(out_path, "w") as f_out:
        for raw_file in raw_dir.glob("*.json"):
            with open(raw_file) as f_in:
                records = json.load(f_in)
            for rec in records:
                text = rec.get("text", "").strip()
                label = rec.get("label", "neutral")
                if text and label in ("positive", "negative", "neutral"):
                    f_out.write(json.dumps({"text": text, "label": label}) + "\n")
                    count += 1

    print(f"✅ Processed {count} sentiment records → {out_path}")


def preprocess_accidents():
    """
    Standardise accident CSV data into a uniform format.
    Input: data/accidents/raw/*.csv
    Output: data/accidents/accidents_clean.csv
    """
    raw_dir = DATA_DIR / "accidents" / "raw"
    out_path = DATA_DIR / "accidents" / "accidents_clean.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["city", "lat", "lng", "severity", "year", "month"]
    count = 0
    with open(out_path, "w", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        for raw_file in raw_dir.glob("*.csv"):
            with open(raw_file, newline="") as f_in:
                reader = csv.DictReader(f_in)
                for row in reader:
                    try:
                        writer.writerow({
                            "city":     row.get("city", ""),
                            "lat":      float(row.get("lat", row.get("latitude", 0))),
                            "lng":      float(row.get("lng", row.get("longitude", 0))),
                            "severity": int(row.get("severity", 1)),
                            "year":     int(row.get("year", 0)),
                            "month":    int(row.get("month", 0)),
                        })
                        count += 1
                    except (ValueError, KeyError):
                        pass

    print(f"✅ Processed {count} accident records → {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["sentiment", "accidents", "all"], default="all")
    args = parser.parse_args()

    if args.type in ("sentiment", "all"):
        preprocess_sentiment()
    if args.type in ("accidents", "all"):
        preprocess_accidents()
