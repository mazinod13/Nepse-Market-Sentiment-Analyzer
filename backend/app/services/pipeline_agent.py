from datetime import date

from sqlalchemy.orm import Session

from app.models.article_company_map import ArticleCompanyMap
from app.models.company import Company
from app.models.company_alias import CompanyAlias
from app.models.company_sentiment_score import CompanySentimentScore
from app.models.market_sentiment_score import MarketSentimentScore
from app.models.news_article import NewsArticle
from app.models.sentiment_event import SentimentEvent
from app.services.company_matcher import match_article_to_companies
from app.services.sentiment_detector import detect_sentiment_events
from app.services.sentiment_scoring import calculate_sentiment_score, get_sentiment_label


def map_article_to_companies(db: Session, article: NewsArticle):
    existing_maps = (
        db.query(ArticleCompanyMap)
        .filter(ArticleCompanyMap.article_id == article.id)
        .all()
    )

    if existing_maps:
        return existing_maps, False

    companies = db.query(Company).all()
    aliases = db.query(CompanyAlias).all()

    matches = match_article_to_companies(
        article=article,
        companies=companies,
        aliases=aliases,
    )

    saved_maps = []

    for match in matches:
        article_company_map = ArticleCompanyMap(
            article_id=article.id,
            company_symbol=match["company_symbol"],
            match_type=match["match_type"],
            confidence=match["confidence"],
        )

        db.add(article_company_map)
        saved_maps.append(article_company_map)

    db.commit()

    for item in saved_maps:
        db.refresh(item)

    return saved_maps, True


def detect_events_for_article(db: Session, article: NewsArticle):
    existing_events = (
        db.query(SentimentEvent)
        .filter(SentimentEvent.article_id == article.id)
        .all()
    )

    if existing_events:
        return existing_events, False

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

    for item in saved_events:
        db.refresh(item)

    return saved_events, True


def calculate_company_sentiment_from_symbol(db: Session, symbol: str):
    symbol = symbol.upper()

    article_maps = (
        db.query(ArticleCompanyMap)
        .filter(ArticleCompanyMap.company_symbol == symbol)
        .all()
    )

    article_ids = [item.article_id for item in article_maps]

    if not article_ids:
        return None

    events = (
        db.query(SentimentEvent)
        .filter(SentimentEvent.article_id.in_(article_ids))
        .all()
    )

    if not events:
        return None

    result = calculate_sentiment_score(events)

    score_record = CompanySentimentScore(
        company_symbol=symbol,
        score=result["score"],
        label=result["label"],
        confidence=result["confidence"],
        score_date=date.today(),
        explanation={
            **result["explanation"],
            "company_symbol": symbol,
            "agent_generated": True,
            "mapped_article_count": len(article_ids),
            "article_ids": article_ids,
        },
    )

    db.add(score_record)
    db.commit()
    db.refresh(score_record)

    return score_record


def calculate_market_sentiment_from_latest_company_scores(db: Session):
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
        return None

    average_score = round(
        sum(item.score for item in latest_company_scores) / len(latest_company_scores)
    )

    average_confidence = round(
        sum(float(item.confidence or 0) for item in latest_company_scores)
        / len(latest_company_scores),
        4,
    )

    market_score = MarketSentimentScore(
        score=average_score,
        label=get_sentiment_label(average_score),
        confidence=average_confidence,
        score_date=date.today(),
        explanation={
            "method": "Agent-generated average of latest company sentiment scores",
            "company_count": len(latest_company_scores),
            "agent_generated": True,
            "companies": [
                {
                    "company_symbol": item.company_symbol,
                    "score": item.score,
                    "label": item.label,
                    "confidence": float(item.confidence or 0),
                }
                for item in latest_company_scores
            ],
        },
    )

    db.add(market_score)
    db.commit()
    db.refresh(market_score)

    return market_score


def run_article_pipeline(db: Session, article_id: int):
    article = (
        db.query(NewsArticle)
        .filter(NewsArticle.id == article_id)
        .first()
    )

    if not article:
        return None

    maps, maps_created = map_article_to_companies(db, article)
    events, events_created = detect_events_for_article(db, article)

    affected_symbols = sorted({item.company_symbol for item in maps})

    company_scores = []

    for symbol in affected_symbols:
        score = calculate_company_sentiment_from_symbol(db, symbol)

        if score:
            company_scores.append(score)

    market_score = calculate_market_sentiment_from_latest_company_scores(db)

    return {
        "article_id": article.id,
        "article_title": article.title,
        "maps_created": maps_created,
        "events_created": events_created,
        "mapped_companies": affected_symbols,
        "event_count": len(events),
        "company_scores": [
            {
                "company_symbol": item.company_symbol,
                "score": item.score,
                "label": item.label,
                "confidence": float(item.confidence or 0),
            }
            for item in company_scores
        ],
        "market_score": {
            "id": market_score.id,
            "score": market_score.score,
            "label": market_score.label,
            "confidence": float(market_score.confidence or 0),
        }
        if market_score
        else None,
    }