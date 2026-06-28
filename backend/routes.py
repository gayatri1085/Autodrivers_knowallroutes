"""
AutoRouteAI — API Router (aggregates all endpoint modules)
"""

from fastapi import APIRouter

from api.navigation import router as nav_router
from api.sentiment import router as sentiment_router
from api.traffic import router as traffic_router

router = APIRouter()

router.include_router(nav_router,       prefix="/api", tags=["Navigation"])
router.include_router(sentiment_router, prefix="/api", tags=["Sentiment"])
router.include_router(traffic_router,   prefix="/api", tags=["Traffic"])
