from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.sql import func

from app.db.database import Base


class ArticleCompanyMap(Base):
    __tablename__ = "article_company_map"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("news_articles.id"), nullable=False, index=True)
    company_symbol = Column(String(50), nullable=False, index=True)
    match_type = Column(String(100), nullable=True)
    confidence = Column(Numeric(5, 4), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())