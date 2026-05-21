import hashlib
import re
from datetime import datetime, timezone
from typing import Any

from app.schemas.scraped_article import ScrapedArticle


def clean_text(value: str | None) -> str | None:
    if not value:
        return None

    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def generate_content_hash(title: str, content: str | None, original_url: str) -> str:
    raw_text = f"{title}|{content or ''}|{original_url}"
    return hashlib.sha256(raw_text.encode("utf-8")).hexdigest()


def detect_language(text: str | None) -> str | None:
    if not text:
        return None

    # Basic Nepali Unicode range detection
    if re.search(r"[\u0900-\u097F]", text):
        return "ne"

    return "en"


def normalize_scraped_article(article: ScrapedArticle) -> dict[str, Any]:
    title = clean_text(article.title)
    summary = clean_text(article.summary)
    content = clean_text(article.content)

    if not title:
        raise ValueError("Scraped article title is required")

    if not article.original_url:
        raise ValueError("Scraped article original_url is required")

    language_code = article.language_code or detect_language(
        f"{title} {summary or ''} {content or ''}"
    )

    content_hash = generate_content_hash(
        title=title,
        content=content,
        original_url=article.original_url,
    )

    return {
        "source_id": article.source_id,
        "original_url": article.original_url,
        "title": title,
        "summary": summary,
        "content": content,
        "language_code": language_code,
        "published_at": article.published_at,
        "author": clean_text(article.author),
        "image_url": article.image_url,
        "tags": article.tags or [],
        "raw_data": {
            **article.raw_data,
            "normalized_at": datetime.now(timezone.utc).isoformat(),
            "source_name": article.source_name,
            "source_type": article.source_type,
        },
        "content_hash": content_hash,
        "status": article.status,
    }