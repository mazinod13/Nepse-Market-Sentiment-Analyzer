from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.article_company_maps import router as article_company_maps_router
from app.api.companies import router as companies_router
from app.api.company_sentiment_scores import router as company_sentiment_scores_router
from app.api.market_sentiment_scores import router as market_sentiment_scores_router
from app.api.news_articles import router as news_articles_router
from app.api.sentiment_events import router as sentiment_events_router
from app.api.sources import router as sources_router
from app.api.company_aliases import router as company_aliases_router
from app.api.agent import router as agent_router
from app.api.scraping_jobs import router as scraping_jobs_router

from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(companies_router)
app.include_router(sources_router)
app.include_router(news_articles_router)
app.include_router(sentiment_events_router)
app.include_router(company_sentiment_scores_router)
app.include_router(article_company_maps_router)
app.include_router(market_sentiment_scores_router)
app.include_router(company_aliases_router)
app.include_router(agent_router)
app.include_router(scraping_jobs_router)

@app.get("/")
def root():
    return {
        "message": "NEPSE Market Sentiment Analyzer API is running",
        "environment": settings.APP_ENV,
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }