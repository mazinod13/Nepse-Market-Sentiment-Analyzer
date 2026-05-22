from app.scrapers.onlinekhabar_scraper import OnlineKhabarScraper
from app.scrapers.bizmandu_scraper import BizmanduScraper
from app.scrapers.nepse_scraper import NepseScraper
from app.scrapers.nepse_company_scraper import NepseCompanyScraper

# Sentinel: pass as `limit` to scrape everything the source offers.
SCRAPE_ALL = 0

# Per-scraper sensible defaults when the caller asks for "a few".
SCRAPER_DEFAULTS: dict[str, int] = {
    "onlinekhabar":        20,
    "bizmandu":            20,
    "nepse":               0,
    "nepse_company":        0,   # company scraper is always "all companies"
}

SCRAPER_REGISTRY = {
    "onlinekhabar":    OnlineKhabarScraper,
    "bizmandu":        BizmanduScraper,
    "nepse":           NepseScraper,
    "nepse_company":   NepseCompanyScraper,
}


def get_scraper(source_id: str):
    scraper_class = SCRAPER_REGISTRY.get(source_id)
    if not scraper_class:
        raise ValueError(f"No scraper registered for source_id: '{source_id}'")
    return scraper_class()


def resolve_limit(source_id: str, requested_limit: int | None) -> int:

    if requested_limit is None or requested_limit == SCRAPE_ALL:
        return SCRAPE_ALL
    if requested_limit == -1:
        return SCRAPER_DEFAULTS.get(source_id, 20)
    return max(1, requested_limit)