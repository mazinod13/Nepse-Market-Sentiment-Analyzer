from app.core.celery_app import celery_app
from app.db.database import SessionLocal
from app.scrapers.registry import get_scraper
from app.services.article_ingestion import save_normalized_article
from app.services.article_normalizer import normalize_scraped_article
from app.services.pipeline_agent import run_article_pipeline


@celery_app.task(name="app.tasks.scraping_tasks.scrape_source")
def scrape_source(source_id: str, limit: int = 10, run_pipeline: bool = True):
    db = SessionLocal()

    try:
        scraper = get_scraper(source_id)
        scraped_articles = scraper.scrape(limit=limit)

        saved_count = 0
        duplicate_count = 0
        failed_count = 0
        saved_article_ids = []
        pipeline_results = []

        for scraped_article in scraped_articles:
            try:
                normalized_article = normalize_scraped_article(scraped_article)

                article, was_created = save_normalized_article(
                    db=db,
                    article_data=normalized_article,
                )

                if was_created:
                    saved_count += 1
                    saved_article_ids.append(article.id)
                else:
                    duplicate_count += 1

                if run_pipeline:
                    pipeline_result = run_article_pipeline(
                        db=db,
                        article_id=article.id,
                    )
                    pipeline_results.append(pipeline_result)

            except Exception as error:
                failed_count += 1
                print(f"Article processing failed: {error}")

        return {
            "source_id": source_id,
            "fetched_count": len(scraped_articles),
            "saved_count": saved_count,
            "duplicate_count": duplicate_count,
            "failed_count": failed_count,
            "saved_article_ids": saved_article_ids,
            "pipeline_results": pipeline_results,
        }

    finally:
        db.close()