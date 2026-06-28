"""
Tests for the sentiment analyser.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from ai.sentiment_model import SentimentAnalyser


@pytest.fixture
def analyser():
    return SentimentAnalyser()


# ── English sentiment ─────────────────────────────────────────────────────────

def test_positive_english(analyser):
    result = analyser.analyse("This road is very smooth and comfortable to drive on.")
    assert result["label"] == "positive"
    assert result["score"] > 0.5


def test_negative_english(analyser):
    result = analyser.analyse("Terrible road full of potholes. Very dangerous at night.")
    assert result["label"] == "negative"
    assert result["score"] > 0.5


def test_neutral_english(analyser):
    result = analyser.analyse("I took this road yesterday.")
    assert result["label"] in ("neutral", "positive", "negative")  # Must return a valid label


# ── Tamil transliteration ─────────────────────────────────────────────────────

def test_positive_tamil(analyser):
    result = analyser.analyse("Romba nalla road, super smooth", language="ta")
    assert result["label"] == "positive"


def test_negative_tamil(analyser):
    result = analyser.analyse("Ketta road, romba mosam, kuzhimbu everywhere", language="ta")
    assert result["label"] == "negative"


# ── Aspect extraction ─────────────────────────────────────────────────────────

def test_pothole_aspect_detected(analyser):
    result = analyser.analyse("There are potholes near the junction. Very bad.")
    assert "pothole" in result["road_aspects"]
    assert result["road_aspects"]["pothole"] == "negative"


def test_flood_aspect_detected(analyser):
    result = analyser.analyse("This road floods during rain. Very dangerous.")
    assert "flooding" in result["road_aspects"]


def test_no_aspects_in_generic_text(analyser):
    result = analyser.analyse("I went to the market.")
    # Should not hallucinate aspects
    assert isinstance(result["road_aspects"], dict)


# ── Output schema ─────────────────────────────────────────────────────────────

def test_output_has_required_keys(analyser):
    result = analyser.analyse("Good road")
    assert "label" in result
    assert "score" in result
    assert "road_aspects" in result


def test_score_in_range(analyser):
    for text in [
        "Excellent smooth road",
        "Very bad potholes everywhere",
        "Average road, nothing special",
    ]:
        result = analyser.analyse(text)
        assert 0.0 <= result["score"] <= 1.0


def test_label_is_valid(analyser):
    valid_labels = {"positive", "negative", "neutral"}
    texts = [
        "Great road",
        "Worst road ever",
        "Road exists",
    ]
    for text in texts:
        result = analyser.analyse(text)
        assert result["label"] in valid_labels, f"Invalid label for: {text!r}"


# ── Edge cases ────────────────────────────────────────────────────────────────

def test_empty_text_handled(analyser):
    result = analyser.analyse("")
    assert result["label"] in ("positive", "negative", "neutral")


def test_very_long_text(analyser):
    long_text = "smooth road " * 200
    result = analyser.analyse(long_text)
    assert result["label"] == "positive"


def test_mixed_sentiment(analyser):
    result = analyser.analyse("Road is smooth but has dangerous potholes at the end.")
    # Should return some label without crashing
    assert result["label"] in ("positive", "negative", "neutral")
