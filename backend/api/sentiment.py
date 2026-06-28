"""
Sentiment API — /sentiment endpoint
Analyse driver feedback text for road/route quality signals.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from ai.sentiment_model import SentimentAnalyser

router = APIRouter()
analyser = SentimentAnalyser()


class SentimentRequest(BaseModel):
    text: str
    language: str = "en"   # en | ta | te | ml | kn


class SentimentResponse(BaseModel):
    label: str             # positive | negative | neutral
    score: float           # confidence 0–1
    road_aspects: dict     # {pothole: negative, shade: positive, ...}


@router.post("/sentiment", response_model=SentimentResponse)
async def analyse_sentiment(req: SentimentRequest):
    """
    Classify driver feedback sentiment and extract road aspects.

    Supports English and transliterated South Indian languages.
    """
    result = analyser.analyse(req.text, language=req.language)
    return SentimentResponse(**result)
