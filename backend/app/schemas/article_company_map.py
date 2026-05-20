from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class ArticleCompanyMapBase(BaseModel):
    article_id: int
    company_symbol: str
    match_type: Optional[str] = None
    confidence: Optional[Decimal] = None


class ArticleCompanyMapCreate(ArticleCompanyMapBase):
    pass


class ArticleCompanyMapResponse(ArticleCompanyMapBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True