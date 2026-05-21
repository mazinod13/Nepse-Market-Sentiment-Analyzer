from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.news_article import NewsArticle
from app.services.pipeline_agent import run_article_pipeline


router = APIRouter(
    prefix="/agent",
    tags=["Agent Pipeline"],
)


@router.post("/articles/{article_id}/run")
def run_pipeline_for_article(article_id: int, db: Session = Depends(get_db)):
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

    result = run_article_pipeline(
        db=db,
        article_id=article_id,
    )

    return result


@router.post("/articles/run-all")
def run_pipeline_for_all_articles(db: Session = Depends(get_db)):
    articles = (
        db.query(NewsArticle)
        .order_by(NewsArticle.created_at.desc())
        .all()
    )

    results = []

    for article in articles:
        result = run_article_pipeline(
            db=db,
            article_id=article.id,
        )

        if result:
            results.append(result)

    return {
        "processed_count": len(results),
        "results": results,
    }