from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.news_article import NewsArticle
from app.models.sentiment_event import SentimentEvent
from app.schemas.sentiment_event import SentimentEventResponse
from app.services.sentiment_detector import detect_sentiment_events


router = APIRouter(
    prefix="/sentiment-events",
    tags=["Sentiment Events"],
)


@router.post("/detect/{article_id}", response_model=list[SentimentEventResponse])
def detect_events_for_article(article_id: int, db: Session = Depends(get_db)):
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

    existing_events = (
        db.query(SentimentEvent)
        .filter(SentimentEvent.article_id == article_id)
        .all()
    )

    if existing_events:
        return existing_events

    detected_events = detect_sentiment_events(
        title=article.title,
        content=article.content,
    )

    saved_events = []

    for event_data in detected_events:
        event = SentimentEvent(
            article_id=article.id,
            event_type=event_data["event_type"],
            sentiment=event_data["sentiment"],
            impact_score=event_data["impact_score"],
            confidence=event_data["confidence"],
            evidence=event_data["evidence"],
        )

        db.add(event)
        saved_events.append(event)

    db.commit()

    for event in saved_events:
        db.refresh(event)

    return saved_events


@router.get("/", response_model=list[SentimentEventResponse])
def list_sentiment_events(db: Session = Depends(get_db)):
    events = (
        db.query(SentimentEvent)
        .order_by(SentimentEvent.created_at.desc())
        .all()
    )
    return events


@router.get("/article/{article_id}", response_model=list[SentimentEventResponse])
def get_events_by_article(article_id: int, db: Session = Depends(get_db)):
    events = (
        db.query(SentimentEvent)
        .filter(SentimentEvent.article_id == article_id)
        .order_by(SentimentEvent.created_at.desc())
        .all()
    )

    return events