from app.scrapers.onlinekhabar_scraper import OnlineKhabarScraper
from app.scrapers.bizmandu_scraper import BizmanduScraper

SCRAPER_REGISTRY = {
    "onlinekhabar": OnlineKhabarScraper,
    "bizmandu": BizmanduScraper,
}


def get_scraper(source_id: str):
    scraper_class = SCRAPER_REGISTRY.get(source_id)

    if not scraper_class:
        raise ValueError(f"No scraper registered for source_id: {source_id}")

    return scraper_class()