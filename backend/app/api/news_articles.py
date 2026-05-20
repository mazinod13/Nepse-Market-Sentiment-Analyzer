import hashlib

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.news_article import NewsArticle
from app.schemas.news_article import NewsArticleCreate, NewsArticleResponse


router = APIRouter(
    prefix="/news",
    tags=["News Articles"],
)


def generate_content_hash(title: str, content: str | None, original_url: str | None) -> str:
    raw_text = f"{title}|{content or ''}|{original_url or ''}"
    return hashlib.sha256(raw_text.encode("utf-8")).hexdigest()


@router.post("/", response_model=NewsArticleResponse)
def create_news_article(
    article_data: NewsArticleCreate,
    db: Session = Depends(get_db),
):
    if article_data.original_url:
        existing_article = (
            db.query(NewsArticle)
            .filter(NewsArticle.original_url == article_data.original_url)
            .first()
        )

        if existing_article:
            raise HTTPException(
                status_code=400,
                detail="News article with this URL already exists",
            )

    content_hash = article_data.content_hash or generate_content_hash(
        title=article_data.title,
        content=article_data.content,
        original_url=article_data.original_url,
    )

    existing_hash = (
        db.query(NewsArticle)
        .filter(NewsArticle.content_hash == content_hash)
        .first()
    )

    if existing_hash:
        raise HTTPException(
            status_code=400,
            detail="Duplicate news article detected",
        )

    article = NewsArticle(
        source_id=article_data.source_id,
        original_url=article_data.original_url,
        title=article_data.title,
        summary=article_data.summary,
        content=article_data.content,
        language_code=article_data.language_code,
        published_at=article_data.published_at,
        author=article_data.author,
        image_url=article_data.image_url,
        tags=article_data.tags,
        raw_data=article_data.raw_data,
        content_hash=content_hash,
        status=article_data.status,
    )

    db.add(article)
    db.commit()
    db.refresh(article)

    return article


@router.get("/", response_model=list[NewsArticleResponse])
def list_news_articles(db: Session = Depends(get_db)):
    articles = (
        db.query(NewsArticle)
        .order_by(NewsArticle.created_at.desc())
        .all()
    )
    return articles


@router.get("/{article_id}", response_model=NewsArticleResponse)
def get_news_article(article_id: int, db: Session = Depends(get_db)):
    article = (
        db.query(NewsArticle)
        .filter(NewsArticle.id == article_id)
        .first()
    )

    if not article:
        raise HTTPException(
            status_code=404,
            detail="News article not found",
        )

    return article