from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.db.database import Base


class CompanyAlias(Base):
    __tablename__ = "company_aliases"

    id = Column(Integer, primary_key=True, index=True)
    company_symbol = Column(
        String(50),
        ForeignKey("companies.symbol"),
        nullable=False,
        index=True,
    )
    alias = Column(String(255), nullable=False, index=True)
    language_code = Column(String(10), nullable=True)
    alias_type = Column(String(50), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())