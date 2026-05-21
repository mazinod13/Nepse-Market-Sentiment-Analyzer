from abc import ABC, abstractmethod

from app.schemas.scraped_article import ScrapedArticle


class BaseScraper(ABC):
    source_id: str
    source_name: str
    base_url: str

    @abstractmethod
    def scrape(self, limit: int = 10) -> list[ScrapedArticle]:
        pass