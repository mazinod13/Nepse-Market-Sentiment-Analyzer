from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.schemas.scraped_article import ScrapedArticle
from app.scrapers.base_scraper import BaseScraper


class BizmanduScraper(BaseScraper):
    source_id = "bizmandu"
    source_name = "Bizmandu"
    base_url = "https://bizmandu.com"

    category_urls = [
        "https://bizmandu.com/content/category/market.html",
        "https://bizmandu.com/content/category/news.html",
        "https://bizmandu.com/content/category/banking.html",
    ]

    headers = {
        "User-Agent": "NepseSentimentBot/0.1 (+research MVP; contact: local-dev)",
        "Accept-Language": "ne,en;q=0.9",
    }

    def scrape(self, limit: int = 10) -> list[ScrapedArticle]:
        articles = []
        seen_urls = set()

        for category_url in self.category_urls:
            if len(articles) >= limit:
                break

            category_articles = self.scrape_category(
                category_url=category_url,
                remaining_limit=limit - len(articles),
            )

            for article in category_articles:
                if article.original_url in seen_urls:
                    continue

                seen_urls.add(article.original_url)
                articles.append(article)

                if len(articles) >= limit:
                    break

        return articles

    def scrape_category(
        self,
        category_url: str,
        remaining_limit: int,
    ) -> list[ScrapedArticle]:
        response = requests.get(
            category_url,
            timeout=20,
            headers=self.headers,
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        articles = []

        cards = soup.select("section.news-content.page-block.category div.news-title.md-title")

        for card in cards:
            if len(articles) >= remaining_limit:
                break

            link_tag = card.select_one("h1.title-lg a")

            if not link_tag:
                continue

            title = link_tag.get("title") or link_tag.get_text(" ", strip=True)
            href = link_tag.get("href")

            if not title or not href:
                continue

            article_url = urljoin(self.base_url, href)

            image_url = None
            image_tag = card.select_one("div.news-img img")
            if image_tag:
                image_url = image_tag.get("src")

            author = None
            author_tag = card.select_one(".left-icon span")
            if author_tag:
                author = author_tag.get_text(" ", strip=True)

            nepali_date = None
            date_tag = card.select_one(".right-icon span")
            if date_tag:
                nepali_date = date_tag.get_text(" ", strip=True)

            detail = self.scrape_article_detail(article_url)

            articles.append(
                ScrapedArticle(
                    source_id=self.source_id,
                    source_name=self.source_name,
                    source_type="news_website",
                    original_url=article_url,
                    title=detail.get("title") or title,
                    summary=detail.get("summary"),
                    content=detail.get("content"),
                    language_code="ne",
                    published_at=None,
                    author=detail.get("author") or author,
                    image_url=detail.get("image_url") or image_url,
                    tags=detail.get("tags", []),
                    raw_data={
                        "scraper": "BizmanduScraper",
                        "category_url": category_url,
                        "nepali_date": nepali_date,
                    },
                    status="scraped",
                )
            )

        return articles

    def scrape_article_detail(self, article_url: str) -> dict:
        try:
            response = requests.get(
                article_url,
                timeout=20,
                headers=self.headers,
            )
            response.raise_for_status()
        except requests.RequestException:
            return {}

        soup = BeautifulSoup(response.text, "lxml")

        title = self.extract_title(soup)
        content = self.extract_content(soup)
        summary = self.extract_summary(content)
        image_url = self.extract_image_url(soup)
        author = self.extract_author(soup)
        tags = self.extract_tags(soup)

        return {
            "title": title,
            "summary": summary,
            "content": content,
            "author": author,
            "image_url": image_url,
            "tags": tags,
        }

    def extract_title(self, soup: BeautifulSoup) -> str | None:
        title_tag = soup.find("h1")

        if title_tag:
            return title_tag.get_text(" ", strip=True)

        og_title = soup.find("meta", property="og:title")
        if og_title:
            return og_title.get("content")

        return None

    def extract_content(self, soup: BeautifulSoup) -> str | None:
        # Bizmandu detail pages may change layout, so we use multiple fallbacks.
        possible_containers = [
            "div.news-detail",
            "div.detail-news",
            "div.single-news",
            "div.post-content",
            "article",
            "section.news-content",
        ]

        paragraphs = []

        for selector in possible_containers:
            container = soup.select_one(selector)

            if not container:
                continue

            paragraphs = [
                paragraph.get_text(" ", strip=True)
                for paragraph in container.find_all("p")
                if paragraph.get_text(" ", strip=True)
            ]

            if paragraphs:
                break

        if not paragraphs:
            paragraphs = [
                paragraph.get_text(" ", strip=True)
                for paragraph in soup.find_all("p")
                if paragraph.get_text(" ", strip=True)
            ]

        if not paragraphs:
            return None

        cleaned_paragraphs = []

        blocked_phrases = [
            "बिजमाण्डू",
            "Facebook",
            "Twitter",
            "LinkedIn",
            "Share",
        ]

        for paragraph in paragraphs:
            if len(paragraph) < 20:
                continue

            if any(blocked in paragraph for blocked in blocked_phrases):
                continue

            cleaned_paragraphs.append(paragraph)

        return "\n".join(cleaned_paragraphs) if cleaned_paragraphs else None

    def extract_summary(self, content: str | None) -> str | None:
        if not content:
            return None

        first_line = content.split("\n")[0].strip()

        return first_line if first_line else None

    def extract_image_url(self, soup: BeautifulSoup) -> str | None:
        og_image = soup.find("meta", property="og:image")

        if og_image:
            return og_image.get("content")

        image_tag = soup.select_one("article img, div.news-detail img, div.post-content img")

        if image_tag:
            src = image_tag.get("src")
            if src:
                return urljoin(self.base_url, src)

        return None

    def extract_author(self, soup: BeautifulSoup) -> str | None:
        author_selectors = [
            ".left-icon span",
            ".author span",
            ".news-author",
            ".post-author",
        ]

        for selector in author_selectors:
            author_tag = soup.select_one(selector)

            if author_tag:
                author = author_tag.get_text(" ", strip=True)
                if author:
                    return author

        return None

    def extract_tags(self, soup: BeautifulSoup) -> list[str]:
        tags = []

        for tag in soup.select("a[rel='tag'], .tags a, .post-tags a"):
            text = tag.get_text(" ", strip=True)

            if text:
                tags.append(text)

        return list(dict.fromkeys(tags))