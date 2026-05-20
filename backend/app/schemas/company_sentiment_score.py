from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel


class CompanySentimentScoreBase(BaseModel):
    company_symbol: str
    score: int
    label: Optional[str] = None
    confidence: Optional[Decimal] = None
    score_date: date
    explanation: Optional[dict[str, Any]] = None


class CompanySentimentScoreCreate(CompanySentimentScoreBase):
    pass


class CompanySentimentScoreResponse(CompanySentimentScoreBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True