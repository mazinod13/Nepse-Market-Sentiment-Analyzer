from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel


class MarketSentimentScoreBase(BaseModel):
    score: int
    label: Optional[str] = None
    confidence: Optional[Decimal] = None
    score_date: date
    explanation: Optional[dict[str, Any]] = None


class MarketSentimentScoreResponse(MarketSentimentScoreBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True