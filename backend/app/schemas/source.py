from decimal import Decimal
from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class SourceBase(BaseModel):
    source_id: str
    source_name: str
    source_type: Optional[str] = None
    website: Optional[str] = None
    language_code: Optional[str] = None
    reliability_score: Optional[Decimal] = None
    is_active: bool = True


class SourceCreate(SourceBase):
    pass


class SourceResponse(SourceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True