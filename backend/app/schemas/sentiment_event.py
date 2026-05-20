from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class SentimentEventBase(BaseModel):
    article_id: int
    event_type: Optional[str] = None
    sentiment: Optional[str] = None
    impact_score: int = 0
    confidence: Optional[Decimal] = None
    evidence: Optional[str] = None


class SentimentEventCreate(SentimentEventBase):
    pass


class SentimentEventResponse(SentimentEventBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True