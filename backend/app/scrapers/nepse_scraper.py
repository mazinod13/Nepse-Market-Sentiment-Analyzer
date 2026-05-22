import asyncio
import re
from datetime import datetime

from app.schemas.scraped_article import ScrapedArticle
from app.scrapers.base_scraper import BaseScraper
from app.services.nepse_normalizer import NepseClient


class NepseScraper(BaseScraper):
    source_id = "nepse"
    source_name = "NEPSE"

    def scrape(self, limit: int = 0) -> list[ScrapedArticle]:
        """Synchronous wrapper. limit=0 means fetch everything."""
        return asyncio.run(self._scrape_async(limit))

    async def _scrape_async(self, limit: int) -> list[ScrapedArticle]:
        async with NepseClient() as nepse:
            news_raw        = await nepse.get_news_and_alerts()
            disclosures_raw = await nepse.get_corporate_disclosures()

        news_raw        = self._unwrap(news_raw)
        disclosures_raw = self._unwrap(disclosures_raw)

        fetch_all = (limit == 0)
        articles: list[ScrapedArticle] = []
        seen_ids: set[str] = set()

        for item in news_raw:
            uid = f"news-{item.get('id')}"
            if uid in seen_ids:
                continue
            seen_ids.add(uid)
            articles.append(self._parse_news_alert(item))
            if not fetch_all and len(articles) >= limit:
                return articles

        for item in disclosures_raw:
            uid = f"disclosure-{item.get('id')}"
            if uid in seen_ids:
                continue
            seen_ids.add(uid)
            articles.append(self._parse_corporate_disclosure(item))
            if not fetch_all and len(articles) >= limit:
                return articles

        return articles

    # -----------------------------------------------------------------------
    # Parsers
    # -----------------------------------------------------------------------

    def _parse_news_alert(self, item: dict) -> ScrapedArticle:
        raw_content = self._strip_html(item.get("messageBody") or "")
        title       = item.get("messageTitle") or ""
        summary     = raw_content[:300] if raw_content else None
        record_id   = item.get("id") or item.get("encryptedId") or ""

        return ScrapedArticle(
            source_id=self.source_id,
            source_name=self.source_name,
            source_type="stock_exchange",
            # Unique per record — prevents all alerts collapsing to one DB row
            original_url=f"https://www.nepalstock.com/news-and-alerts#{record_id}",
            title=title,
            summary=summary,
            content=raw_content or None,
            language_code=self._detect_language(title),
            published_at=self._parse_dt(item.get("addedDate")),
            author="NEPSE",
            image_url=None,
            tags=["nepse", "notice"],
            raw_data={
                "scraper":       "NepseScraper",
                "record_type":   "news_alert",
                "id":            item.get("id"),
                "expiry_date":   item.get("expiryDate"),
                "encrypted_id":  item.get("encryptedId"),
                "approved_date": item.get("approvedDate"),
                "remarks":       item.get("remarks"),
            },
            status="scraped",
        )

    def _parse_corporate_disclosure(self, item: dict) -> ScrapedArticle:
        raw_content   = self._strip_html(item.get("newsBody") or "")
        title         = item.get("newsHeadline") or ""
        summary       = raw_content[:300] if raw_content else None
        symbol        = item.get("symbol")
        security_name = item.get("securityName") or item.get("companyName") or ""
        record_id     = item.get("id") or ""

        tags = ["nepse", "disclosure"]
        if symbol:
            tags.append(symbol.lower())

        return ScrapedArticle(
            source_id=self.source_id,
            source_name=self.source_name,
            source_type="stock_exchange",
            # Unique per record
            original_url=f"https://www.nepalstock.com/corporatedisclosures#{record_id}",
            title=title,
            summary=summary,
            content=raw_content or None,
            language_code=self._detect_language(title),
            published_at=self._parse_dt(item.get("publishedDate")),
            author=security_name or "NEPSE",
            image_url=None,
            tags=tags,
            raw_data={
                "scraper":            "NepseScraper",
                "record_type":        "corporate_disclosure",
                "id":                 item.get("id"),
                "security_id":        item.get("securityId"),
                "symbol":             symbol,
                "security_name":      security_name,
                "board_meeting_date": item.get("boardMeetingDate"),
                "approved_date":      item.get("approvedDate"),
            },
            status="scraped",
        )

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _unwrap(raw) -> list:
        if isinstance(raw, list):
            return raw
        if isinstance(raw, dict):
            for key in ("data", "content", "result", "items"):
                if isinstance(raw.get(key), list):
                    return raw[key]
        return []

    _FILE_BASE = "https://www.nepalstock.com/api/nots/nepse-data/nepse-file"

    def _build_file_url(self, file_path: str | None) -> str | None:
        return f"{self._FILE_BASE}/{file_path}" if file_path else None

    @staticmethod
    def _strip_html(html: str) -> str:
        text = re.sub(r"<[^>]+>", " ", html)
        for entity, rep in [("&nbsp;", " "), ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">")]:
            text = text.replace(entity, rep)
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _parse_dt(value: str | None) -> datetime | None:
        if not value:
            return None
        for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return None

    @staticmethod
    def _detect_language(text: str) -> str:
        return "ne" if re.search(r"[\u0900-\u097F]", text) else "en"