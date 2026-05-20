from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class NewsArticleBase(BaseModel):
    source_id: Optional[str] = None
    original_url: Optional[str] = None
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    language_code: Optional[str] = None
    published_at: Optional[datetime] = None
    author: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[list[str]] = None
    raw_data: Optional[dict[str, Any]] = None
    content_hash: Optional[str] = None
    status: Optional[str] = "draft"


class NewsArticleCreate(NewsArticleBase):
    pass


class NewsArticleResponse(NewsArticleBase):
    id: int
    scraped_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True