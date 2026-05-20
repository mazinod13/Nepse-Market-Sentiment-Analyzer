from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.company_sentiment_score import CompanySentimentScore
from app.models.market_sentiment_score import MarketSentimentScore
from app.schemas.market_sentiment_score import MarketSentimentScoreResponse
from app.services.sentiment_scoring import get_sentiment_label


router = APIRouter(
    prefix="/sentiment/market",
    tags=["Market Sentiment"],
)


@router.post("/calculate", response_model=MarketSentimentScoreResponse)
def calculate_market_sentiment(db: Session = Depends(get_db)):
    latest_company_scores = []

    company_symbols = (
        db.query(CompanySentimentScore.company_symbol)
        .distinct()
        .all()
    )

    for item in company_symbols:
        symbol = item[0]

        latest_score = (
            db.query(CompanySentimentScore)
            .filter(CompanySentimentScore.company_symbol == symbol)
            .order_by(CompanySentimentScore.created_at.desc())
            .first()
        )

        if latest_score:
            latest_company_scores.append(latest_score)

    if not latest_company_scores:
        raise HTTPException(
            status_code=404,
            detail="No company sentiment scores found",
        )

    average_score = round(
        sum(item.score for item in latest_company_scores) / len(latest_company_scores)
    )

    average_confidence = round(
        sum(float(item.confidence or 0) for item in latest_company_scores)
        / len(latest_company_scores),
        4,
    )

    label = get_sentiment_label(average_score)

    explanation = {
        "method": "Average of latest company sentiment scores",
        "company_count": len(latest_company_scores),
        "companies": [
            {
                "company_symbol": item.company_symbol,
                "score": item.score,
                "label": item.label,
                "confidence": float(item.confidence or 0),
            }
            for item in latest_company_scores
        ],
    }

    market_score = MarketSentimentScore(
        score=average_score,
        label=label,
        confidence=average_confidence,
        score_date=date.today(),
        explanation=explanation,
    )

    db.add(market_score)
    db.commit()
    db.refresh(market_score)

    return market_score


@router.get("/latest", response_model=MarketSentimentScoreResponse)
def get_latest_market_sentiment(db: Session = Depends(get_db)):
    market_score = (
        db.query(MarketSentimentScore)
        .order_by(MarketSentimentScore.created_at.desc())
        .first()
    )

    if not market_score:
        raise HTTPException(
            status_code=404,
            detail="No market sentiment score found",
        )

    return market_score


@router.get("/timeline", response_model=list[MarketSentimentScoreResponse])
def get_market_sentiment_timeline(db: Session = Depends(get_db)):
    scores = (
        db.query(MarketSentimentScore)
        .order_by(MarketSentimentScore.score_date.asc())
        .all()
    )

    return scores