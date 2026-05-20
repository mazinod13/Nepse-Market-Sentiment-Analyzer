from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.database import Base


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String(100), nullable=True, index=True)
    original_url = Column(String(1000), unique=True, nullable=True)
    title = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    language_code = Column(String(10), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    author = Column(String(255), nullable=True)
    image_url = Column(String(1000), nullable=True)
    tags = Column(JSONB, nullable=True)
    raw_data = Column(JSONB, nullable=True)
    content_hash = Column(String(128), nullable=True, index=True)
    status = Column(String(50), default="draft")

    created_at = Column(DateTime(timezone=True), server_default=func.now())