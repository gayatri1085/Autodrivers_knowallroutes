"""
SQLAlchemy async ORM models.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy import BigInteger, Float, Integer, SmallInteger, String, Text, DateTime
import os


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://autorouteai:autorouteai_secret@localhost:5432/autorouteai"
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class RoadSegment(Base):
    __tablename__ = "road_segments"

    id:           Mapped[int]   = mapped_column(BigInteger, primary_key=True)
    way_id:       Mapped[int]   = mapped_column(BigInteger, unique=True, nullable=True)
    city:         Mapped[str]   = mapped_column(String(64))
    name:         Mapped[str]   = mapped_column(Text, nullable=True)
    highway_type: Mapped[str]   = mapped_column(String(64), nullable=True)
    road_score:   Mapped[float] = mapped_column(Float, default=0.5)
    driver_score: Mapped[float] = mapped_column(Float, default=0.5)
    accident_risk:Mapped[float] = mapped_column(Float, default=0.0)
    flood_risk:   Mapped[float] = mapped_column(Float, default=0.0)


class DriverFeedback(Base):
    __tablename__ = "driver_feedback"

    id:         Mapped[str]   = mapped_column(String(36), primary_key=True)
    route_id:   Mapped[str]   = mapped_column(String(128), nullable=True)
    city:       Mapped[str]   = mapped_column(String(64), nullable=True)
    rating:     Mapped[int]   = mapped_column(SmallInteger)
    comment:    Mapped[str]   = mapped_column(Text, nullable=True)
    sentiment:  Mapped[str]   = mapped_column(String(16), nullable=True)


async def init_db():
    """Create tables if they don't exist (dev convenience — use Alembic in production)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
