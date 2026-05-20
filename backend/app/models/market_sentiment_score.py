from sqlalchemy import Column, Date, DateTime, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.database import Base


class MarketSentimentScore(Base):
    __tablename__ = "market_sentiment_scores"

    id = Column(Integer, primary_key=True, index=True)
    score = Column(Integer, nullable=False)
    label = Column(String(100), nullable=True)
    confidence = Column(Numeric(5, 4), nullable=True)
    score_date = Column(Date, nullable=False)
    explanation = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())