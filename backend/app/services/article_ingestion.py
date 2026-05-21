from sqlalchemy.orm import Session

from app.models.news_article import NewsArticle


def save_normalized_article(db: Session, article_data: dict):
    if article_data.get("original_url"):
        existing_url = (
            db.query(NewsArticle)
            .filter(NewsArticle.original_url == article_data["original_url"])
            .first()
        )

        if existing_url:
            return existing_url, False

    if article_data.get("content_hash"):
        existing_hash = (
            db.query(NewsArticle)
            .filter(NewsArticle.content_hash == article_data["content_hash"])
            .first()
        )

        if existing_hash:
            return existing_hash, False

    article = NewsArticle(**article_data)

    db.add(article)
    db.commit()
    db.refresh(article)

    return article, True