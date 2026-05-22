from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class ScrapedArticle(BaseModel):
    source_id: str
    source_name: Optional[str] = None
    source_type: Optional[str] = "news_website"

    original_url: Optional[str] = None
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    language_code: Optional[str] = None
    published_at: Optional[datetime] = None
    author: Optional[str] = None
    image_url: Optional[str] = None
    tags: list[str] = []

    raw_data: dict[str, Any] = {}
    status: str = "scraped"