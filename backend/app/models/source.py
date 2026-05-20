from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String
from sqlalchemy.sql import func

from app.db.database import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String(100), unique=True, nullable=False, index=True)
    source_name = Column(String(255), nullable=False)
    source_type = Column(String(100), nullable=True)
    website = Column(String(500), nullable=True)
    language_code = Column(String(10), nullable=True)
    reliability_score = Column(Numeric(4, 2), nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())