from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.article_company_map import ArticleCompanyMap
from app.models.company import Company
from app.models.news_article import NewsArticle
from app.schemas.article_company_map import ArticleCompanyMapResponse
from app.services.company_matcher import match_article_to_companies


router = APIRouter(
    prefix="/article-company-maps",
    tags=["Article Company Mapping"],
)


@router.post("/match/{article_id}", response_model=list[ArticleCompanyMapResponse])
def match_article_companies(article_id: int, db: Session = Depends(get_db)):
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

    existing_maps = (
        db.query(ArticleCompanyMap)
        .filter(ArticleCompanyMap.article_id == article_id)
        .all()
    )

    if existing_maps:
        return existing_maps

    companies = db.query(Company).all()

    matches = match_article_to_companies(
        article=article,
        companies=companies,
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

    return saved_maps


@router.get("/", response_model=list[ArticleCompanyMapResponse])
def list_article_company_maps(db: Session = Depends(get_db)):
    maps = (
        db.query(ArticleCompanyMap)
        .order_by(ArticleCompanyMap.created_at.desc())
        .all()
    )

    return maps


@router.get("/article/{article_id}", response_model=list[ArticleCompanyMapResponse])
def get_maps_by_article(article_id: int, db: Session = Depends(get_db)):
    maps = (
        db.query(ArticleCompanyMap)
        .filter(ArticleCompanyMap.article_id == article_id)
        .order_by(ArticleCompanyMap.created_at.desc())
        .all()
    )

    return maps


@router.get("/company/{symbol}", response_model=list[ArticleCompanyMapResponse])
def get_maps_by_company(symbol: str, db: Session = Depends(get_db)):
    maps = (
        db.query(ArticleCompanyMap)
        .filter(ArticleCompanyMap.company_symbol == symbol.upper())
        .order_by(ArticleCompanyMap.created_at.desc())
        .all()
    )

    return maps