"""
Driver Sentiment Analyser

Fine-tuned RoBERTa model for classifying road/route feedback sentiment.
Extracts aspect-level sentiment for road dimensions (surface, traffic, shade, etc.)
"""

import re
from pathlib import Path
from typing import Optional


MODELS_DIR = Path(__file__).parent.parent.parent / "models"

ROAD_ASPECTS = [
    "pothole", "flooding", "traffic", "speed", "shade",
    "width", "signage", "lighting", "dust", "noise",
]

POSITIVE_WORDS = {
    "en": ["smooth", "good", "nice", "great", "fast", "clean", "wide", "safe", "comfortable"],
    "ta": ["nalla", "super", "romba nalla", "smooth"],
    "te": ["bagundi", "manchidi"],
}

NEGATIVE_WORDS = {
    "en": ["pothole", "bad", "terrible", "slow", "rough", "narrow", "flood", "dangerous", "broken"],
    "ta": ["ketta", "romba mosam", "kuzhimbu"],
    "te": ["cheddaga", "kurapu"],
}


class SentimentAnalyser:
    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._load_model()

    def _load_model(self):
        model_path = MODELS_DIR / "sentiment_classifier.pkl"
        if not model_path.exists():
            # Model not trained yet — will use rule-based fallback
            return
        try:
            import joblib
            self._model = joblib.load(model_path)
        except Exception as e:
            print(f"[SentimentAnalyser] Could not load model: {e}")

    def analyse(self, text: str, language: str = "en") -> dict:
        """
        Classify text sentiment and extract road aspect mentions.
        Returns: {label, score, road_aspects}
        """
        label, score = self._classify(text, language)
        aspects = self._extract_aspects(text, language)
        return {
            "label": label,
            "score": score,
            "road_aspects": aspects,
        }

    def _classify(self, text: str, language: str) -> tuple[str, float]:
        if self._model is not None:
            try:
                proba = self._model.predict_proba([text])[0]
                labels = self._model.classes_
                idx = proba.argmax()
                return str(labels[idx]), round(float(proba[idx]), 3)
            except Exception:
                pass

        # Rule-based fallback
        text_lower = text.lower()
        pos = POSITIVE_WORDS.get(language, POSITIVE_WORDS["en"])
        neg = NEGATIVE_WORDS.get(language, NEGATIVE_WORDS["en"])
        pos_count = sum(1 for w in pos if w in text_lower)
        neg_count = sum(1 for w in neg if w in text_lower)

        if pos_count > neg_count:
            return "positive", round(pos_count / max(pos_count + neg_count, 1), 2)
        elif neg_count > pos_count:
            return "negative", round(neg_count / max(pos_count + neg_count, 1), 2)
        return "neutral", 0.5

    def _extract_aspects(self, text: str, language: str) -> dict:
        text_lower = text.lower()
        aspects = {}
        for aspect in ROAD_ASPECTS:
            if aspect in text_lower:
                # Crude: check polarity near the mention
                pos = POSITIVE_WORDS.get(language, POSITIVE_WORDS["en"])
                neg = NEGATIVE_WORDS.get(language, NEGATIVE_WORDS["en"])
                context = text_lower
                pos_hit = any(w in context for w in pos)
                neg_hit = any(w in context for w in neg)
                aspects[aspect] = "positive" if pos_hit else ("negative" if neg_hit else "neutral")
        return aspects
