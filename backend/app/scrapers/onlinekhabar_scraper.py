from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.schemas.scraped_article import ScrapedArticle
from app.scrapers.base_scraper import BaseScraper


class OnlineKhabarScraper(BaseScraper):
    source_id = "onlinekhabar"
    source_name = "Onlinekhabar"
    base_url = "https://www.onlinekhabar.com"

    def scrape(self, limit: int = 10) -> list[ScrapedArticle]:
        response = requests.get(
            self.base_url,
            timeout=20,
            headers={
                "User-Agent": "NepseSentimentBot/0.1 (+research MVP)",
            },
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        articles = []
        seen_urls = set()

        # Site-specific extraction logic.
        # This selector may need adjustment if OnlineKhabar changes layout.
        links = soup.select("a")

        for link in links:
            if len(articles) >= limit:
                break

            title = link.get_text(" ", strip=True)
            href = link.get("href")

            if not title or not href:
                continue

            article_url = urljoin(self.base_url, href)

            if article_url in seen_urls:
                continue

            if "onlinekhabar.com" not in article_url:
                continue

            # Avoid very short menu/navigation links
            if len(title) < 20:
                continue

            seen_urls.add(article_url)

            article_detail = self.scrape_article_detail(article_url)

            articles.append(
                ScrapedArticle(
                    source_id=self.source_id,
                    source_name=self.source_name,
                    source_type="news_website",
                    original_url=article_url,
                    title=article_detail.get("title") or title,
                    summary=article_detail.get("summary"),
                    content=article_detail.get("content"),
                    language_code="ne",
                    published_at=article_detail.get("published_at"),
                    author=article_detail.get("author"),
                    image_url=article_detail.get("image_url"),
                    tags=article_detail.get("tags", []),
                    raw_data={
                        "scraper": "OnlineKhabarScraper",
                    },
                    status="scraped",
                )
            )

        return articles

    def scrape_article_detail(self, url: str) -> dict:
        try:
            response = requests.get(
                url,
                timeout=20,
                headers={
                    "User-Agent": "NepseSentimentBot/0.1 (+research MVP)",
                },
            )
            response.raise_for_status()
        except requests.RequestException:
            return {}

        soup = BeautifulSoup(response.text, "lxml")

        title = None
        title_tag = soup.find("h1")
        if title_tag:
            title = title_tag.get_text(" ", strip=True)

        paragraphs = [
            p.get_text(" ", strip=True)
            for p in soup.find_all("p")
            if p.get_text(" ", strip=True)
        ]

        content = "\n".join(paragraphs)

        image_url = None
        image_tag = soup.find("meta", property="og:image")
        if image_tag:
            image_url = image_tag.get("content")

        return {
            "title": title,
            "summary": paragraphs[0] if paragraphs else None,
            "content": content,
            "published_at": None,
            "author": None,
            "image_url": image_url,
            "tags": [],
        }