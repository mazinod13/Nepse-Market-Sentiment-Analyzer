from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.sql import func

from app.db.database import Base


class SentimentEvent(Base):
    __tablename__ = "sentiment_events"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("news_articles.id"), nullable=False)
    event_type = Column(String(100), nullable=True)
    sentiment = Column(String(50), nullable=True)
    impact_score = Column(Integer, nullable=False, default=0)
    confidence = Column(Numeric(5, 4), nullable=True)
    evidence = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())