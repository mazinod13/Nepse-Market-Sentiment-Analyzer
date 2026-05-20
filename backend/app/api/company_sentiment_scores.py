from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.article_company_map import ArticleCompanyMap
from app.models.company import Company
from app.models.company_sentiment_score import CompanySentimentScore
from app.models.news_article import NewsArticle
from app.models.sentiment_event import SentimentEvent
from app.schemas.company_sentiment_score import CompanySentimentScoreResponse
from app.services.sentiment_detector import detect_sentiment_events
from app.services.sentiment_scoring import calculate_sentiment_score


router = APIRouter(
    prefix="/sentiment/company",
    tags=["Company Sentiment"],
)


@router.post("/{symbol}/calculate", response_model=CompanySentimentScoreResponse)
def calculate_company_sentiment(symbol: str, db: Session = Depends(get_db)):
    symbol = symbol.upper()

    company = (
        db.query(Company)
        .filter(Company.symbol == symbol)
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )

    article_maps = (
        db.query(ArticleCompanyMap)
        .filter(ArticleCompanyMap.company_symbol == symbol)
        .all()
    )

    if not article_maps:
        raise HTTPException(
            status_code=404,
            detail="No mapped news articles found for this company",
        )

    article_ids = [item.article_id for item in article_maps]

    articles = (
        db.query(NewsArticle)
        .filter(NewsArticle.id.in_(article_ids))
        .all()
    )

    all_events = []

    for article in articles:
        existing_events = (
            db.query(SentimentEvent)
            .filter(SentimentEvent.article_id == article.id)
            .all()
        )

        if existing_events:
            all_events.extend(existing_events)
            continue

        detected_events = detect_sentiment_events(
            title=article.title,
            content=article.content,
        )

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
            all_events.append(event)

    db.commit()

    for event in all_events:
        db.refresh(event)

    result = calculate_sentiment_score(all_events)

    score_record = CompanySentimentScore(
        company_symbol=symbol,
        score=result["score"],
        label=result["label"],
        confidence=result["confidence"],
        score_date=date.today(),
        explanation={
            **result["explanation"],
            "company_symbol": symbol,
            "company_name": company.company_name,
            "mapped_article_count": len(article_ids),
            "article_ids": article_ids,
        },
    )

    db.add(score_record)
    db.commit()
    db.refresh(score_record)

    return score_record


@router.get("/{symbol}/latest", response_model=CompanySentimentScoreResponse)
def get_latest_company_sentiment(symbol: str, db: Session = Depends(get_db)):
    symbol = symbol.upper()

    score_record = (
        db.query(CompanySentimentScore)
        .filter(CompanySentimentScore.company_symbol == symbol)
        .order_by(CompanySentimentScore.created_at.desc())
        .first()
    )

    if not score_record:
        raise HTTPException(
            status_code=404,
            detail="No sentiment score found for this company",
        )

    return score_record


@router.get("/{symbol}/timeline", response_model=list[CompanySentimentScoreResponse])
def get_company_sentiment_timeline(symbol: str, db: Session = Depends(get_db)):
    symbol = symbol.upper()

    scores = (
        db.query(CompanySentimentScore)
        .filter(CompanySentimentScore.company_symbol == symbol)
        .order_by(CompanySentimentScore.score_date.asc())
        .all()
    )

    return scores