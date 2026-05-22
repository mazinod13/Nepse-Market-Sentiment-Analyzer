

import asyncio
import json
import logging
import pathlib
import re
from datetime import datetime
from decimal import Decimal

from app.schemas.scraped_article import ScrapedArticle
from app.schemas.agm_report import (
    AgmReportCreate,
    AgmNoticeSchema,
    AgmDocumentSchema,
)
from app.schemas.financials_report import (
    FinancialReportCreate,
    QuarterMasterSchema,
    ReportTypeMasterSchema,
    FinancialYearSchema,
    FinancialDocumentSchema,
)
from app.schemas.corporate_action import CorporateActionCreate
from app.scrapers.base_scraper import BaseScraper
from app.services.nepse_normalizer import NepseClient

logger = logging.getLogger(__name__)

_FILE_BASE = "https://www.nepalstock.com/api/nots/nepse-data/nepse-file"

COMPANY_MAPPING_PATH = pathlib.Path(__file__).resolve().parent / "data" / "company_mapping.json"


# ── Result container ──────────────────────────────────────────────────────────

class ScrapeResult:
    """Holds both the generic ScrapedArticle and the typed schema for one record."""

    __slots__ = ("article", "typed")

    def __init__(self, article: ScrapedArticle, typed):
        self.article = article   # ScrapedArticle  — for existing pipeline
        self.typed   = typed     # AgmReportCreate | FinancialReportCreate | CorporateActionCreate


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_company_mapping(path: pathlib.Path = COMPANY_MAPPING_PATH) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    for entity, replacement in [("&nbsp;", " "), ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">")]:
        text = text.replace(entity, replacement)
    return re.sub(r"\s+", " ", text).strip()


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _parse_date(value: str | None):
    """Return a date (not datetime) or None."""
    dt = _parse_dt(value)
    return dt.date() if dt else None


def _detect_language(text: str) -> str:
    return "ne" if re.search(r"[\u0900-\u097F]", text) else "en"


def _build_file_url(file_path: str | None) -> str | None:
    return f"{_FILE_BASE}/{file_path}" if file_path else None


def _doc_urls(doc_list: list[dict]) -> list[str]:
    return [_build_file_url(d["filePath"]) for d in (doc_list or []) if d.get("filePath")]


def _to_decimal(value) -> Decimal | None:
    try:
        return Decimal(str(value)) if value is not None else None
    except Exception:
        return None


# ── Main scraper ─────────────────────────────────────────────────────────────

class NepseCompanyScraper(BaseScraper):
    source_id = "nepse"
    source_name = "NEPSE"

    def __init__(self, company_mapping: list[dict] | None = None):
        self._companies = company_mapping or _load_company_mapping()

    # ── Public entry points ───────────────────────────────────────────────────

    def scrape(self, limit: int = 0) -> list[ScrapedArticle]:
        """
        Backward-compatible: returns only ScrapedArticle list.
        limit=0 → all companies.
        """
        return [r.article for r in self.scrape_typed(limit)]

    def scrape_typed(self, limit: int = 0) -> list[ScrapeResult]:
        """
        Returns ScrapeResult list — each has .article (ScrapedArticle)
        and .typed (AgmReportCreate | FinancialReportCreate | CorporateActionCreate).
        """
        return asyncio.run(self._scrape_async(limit))

    # ── Async core ────────────────────────────────────────────────────────────

    async def _scrape_async(self, limit: int) -> list[ScrapeResult]:
        companies = self._companies if not limit else self._companies[:limit]
        results: list[ScrapeResult] = []

        async with NepseClient() as nepse:
            for company in companies:
                sec_id = company["id"]
                symbol = company["symbol"]
                logger.info("Fetching %s (id=%s) …", symbol, sec_id)

                agm_raw, fin_raw, actions_raw = await asyncio.gather(
                    self._safe_fetch(nepse.get_agm_reports, symbol),
                    self._safe_fetch(nepse.get_financials_reports, symbol),
                    self._safe_fetch(nepse.get_corporate_actions, sec_id),
                )

                for item in agm_raw or []:
                    results.append(self._parse_agm(item, company))

                for item in fin_raw or []:
                    results.append(self._parse_financial_report(item, company))

                for item in actions_raw or []:
                    results.append(self._parse_corporate_action(item, company))

        return results

    @staticmethod
    async def _safe_fetch(fn, *args):
        try:
            result = await fn(*args)
            return result if isinstance(result, list) else []
        except Exception as exc:
            logger.warning("Fetch failed (%s %s): %s", fn.__name__, args, exc)
            return []

    # ── AGM parser ────────────────────────────────────────────────────────────

    def _parse_agm(self, item: dict, company: dict) -> ScrapeResult:
        news = item.get("companyNews") or {}
        agm  = news.get("agmNotice") or {}
        docs = item.get("applicationDocumentDetailsList") or []

        symbol       = company["symbol"]
        security_id  = company["id"]
        security_name = company.get("securityName", symbol)
        headline     = news.get("newsHeadline") or f"AGM Notice [{symbol}]"
        raw_body     = _strip_html(news.get("newsBody") or "")

        # ── Typed schema ──────────────────────────────────────────────────────
        agm_notice_schema = AgmNoticeSchema(
            id=agm.get("id"),
            agm_type=agm.get("agmType"),
            agm_date=_parse_date(agm.get("agmDate")),
            agm_no=agm.get("agmNo"),
            book_close_date=_parse_date(agm.get("bookCloseDate")),
            cash_dividend=_to_decimal(agm.get("cashDividend")),
            bonus_share=_to_decimal(agm.get("bonusShare")),
            agenda=agm.get("agenda") or None,
            venue=agm.get("venue") or None,
            remarks=agm.get("remarks") or None,
        )

        doc_schemas = [
            AgmDocumentSchema(
                id=d.get("id"),
                file_path=d.get("filePath"),
                encrypted_id=d.get("encryptedId"),
                submitted_date=_parse_date(d.get("submittedDate")),
                document_type=d.get("documentType"),
            )
            for d in docs
        ]

        typed = AgmReportCreate(
            symbol=symbol,
            security_id=security_id,
            security_name=security_name,
            news_headline=headline,
            news_body=raw_body or None,
            news_type=news.get("newsType"),
            news_source=news.get("newsSource"),
            language_code=_detect_language(headline),
            # Flattened AGM fields for easy DB columns
            agm_type=agm.get("agmType"),
            agm_no=agm.get("agmNo"),
            agm_date=_parse_date(agm.get("agmDate")),
            book_close_date=_parse_date(agm.get("bookCloseDate")),
            cash_dividend=_to_decimal(agm.get("cashDividend")),
            bonus_share=_to_decimal(agm.get("bonusShare")),
            venue=agm.get("venue") or None,
            agenda=agm.get("agenda") or None,
            published_at=_parse_dt(news.get("addedDate")),
            expiry_date=_parse_date(news.get("expiryDate")),
            agm_notice=agm_notice_schema,
            documents=doc_schemas,
            application_id=item.get("id"),
            application_status=item.get("applicationStatus"),
        )

        # ── ScrapedArticle (existing pipeline) ────────────────────────────────
        agm_lines = [
            f"{label}: {val}"
            for label, val in [
                ("AGM Type",      agm.get("agmType")),
                ("AGM Date",      agm.get("agmDate")),
                ("AGM No",        agm.get("agmNo")),
                ("Book Close",    agm.get("bookCloseDate")),
                ("Cash Dividend", agm.get("cashDividend")),
                ("Bonus Shares",  agm.get("bonusShare")),
                ("Venue",         agm.get("venue")),
            ]
            if val not in (None, "", 0)
        ]
        content = "\n".join(filter(None, [raw_body] + agm_lines)) or None

        article = ScrapedArticle(
            source_id=self.source_id,
            source_name=self.source_name,
            source_type="stock_exchange",
            original_url=_doc_urls(docs)[0] if docs else None,
            title=headline,
            summary=raw_body[:300] or (agm_lines[0] if agm_lines else None),
            content=content,
            language_code=_detect_language(headline),
            published_at=_parse_dt(news.get("addedDate")),
            author=security_name,
            image_url=None,
            tags=["nepse", "agm", symbol.lower()],
            raw_data={
                "scraper": "NepseCompanyScraper",
                "record_type": "agm_report",
                "application_id": item.get("id"),
                "symbol": symbol,
                "security_id": security_id,
                "news_type": news.get("newsType"),
                "agm_date": agm.get("agmDate"),
                "agm_no": agm.get("agmNo"),
                "book_close_date": agm.get("bookCloseDate"),
                "cash_dividend": agm.get("cashDividend"),
                "bonus_share": agm.get("bonusShare"),
                "venue": agm.get("venue"),
                "document_urls": _doc_urls(docs),
                "expiry_date": news.get("expiryDate"),
            },
            status="scraped",
        )

        return ScrapeResult(article=article, typed=typed)

    # ── Financial report parser ───────────────────────────────────────────────

    def _parse_financial_report(self, item: dict, company: dict) -> ScrapeResult:
        report = item.get("fiscalReport") or {}
        docs   = item.get("applicationDocumentDetailsList") or []

        symbol        = company["symbol"]
        security_id   = company["id"]
        security_name = company.get("securityName", symbol)

        qm  = report.get("quarterMaster") or {}
        rtm = report.get("reportTypeMaster") or {}
        fy  = report.get("financialYear") or {}

        quarter_name = qm.get("quarterName", "")
        report_type  = rtm.get("reportName", "Report")
        fy_name      = fy.get("fyName", "")

        # ── Typed schema ──────────────────────────────────────────────────────
        doc_schemas = [
            FinancialDocumentSchema(
                id=d.get("id"),
                file_path=d.get("filePath"),
                encrypted_id=d.get("encryptedId"),
                submitted_date=_parse_date(d.get("submittedDate")),
                document_type=d.get("documentType"),
            )
            for d in docs
        ]

        typed = FinancialReportCreate(
            symbol=symbol,
            security_id=security_id,
            security_name=security_name,
            # Quarter
            quarter_id=qm.get("id"),
            quarter_name=quarter_name or None,
            # Report type
            report_type_id=rtm.get("id"),
            report_type_name=report_type or None,
            # Fiscal year
            fiscal_year_id=fy.get("id"),
            fiscal_year=fy_name or None,
            fiscal_year_nepali=fy.get("fyNameNepali") or None,
            # Metrics
            eps=_to_decimal(report.get("epsValue")),
            pe=_to_decimal(report.get("peValue")),
            net_worth_per_share=_to_decimal(report.get("netWorthPerShare")),
            paid_up_capital=_to_decimal(report.get("paidUpCapital")),
            profit_amount=_to_decimal(report.get("profitAmount")),
            remarks=report.get("remarks") or None,
            published_at=_parse_dt(item.get("modifiedDate")),
            # Nested
            quarter_master=QuarterMasterSchema(
                id=qm.get("id"),
                quarter_name=qm.get("quarterName"),
            ) if qm else None,
            report_type_master=ReportTypeMasterSchema(
                id=rtm.get("id"),
                report_name=rtm.get("reportName"),
            ) if rtm else None,
            financial_year=FinancialYearSchema(
                id=fy.get("id"),
                fy_name=fy.get("fyName"),
                fy_name_nepali=fy.get("fyNameNepali"),
                from_year=_parse_date(fy.get("fromYear")),
                to_year=_parse_date(fy.get("toYear")),
            ) if fy else None,
            documents=doc_schemas,
            application_id=item.get("id"),
            fiscal_report_id=report.get("id"),
            application_status=item.get("applicationStatus"),
        )

        # ── ScrapedArticle ────────────────────────────────────────────────────
        title = f"{quarter_name} {report_type} FY{fy_name} [{symbol}]".strip()
        fin_lines = [
            f"{label}: {val}"
            for label, val in [
                ("EPS",             report.get("epsValue")),
                ("PE Ratio",        report.get("peValue")),
                ("Net Worth/Share", report.get("netWorthPerShare")),
                ("Paid-up Capital", report.get("paidUpCapital")),
                ("Net Profit",      report.get("profitAmount")),
            ]
            if val is not None
        ]

        article = ScrapedArticle(
            source_id=self.source_id,
            source_name=self.source_name,
            source_type="stock_exchange",
            original_url=_doc_urls(docs)[0] if docs else None,
            title=title,
            summary=fin_lines[0] if fin_lines else None,
            content="\n".join(fin_lines) or None,
            language_code="en",
            published_at=_parse_dt(item.get("modifiedDate")),
            author=security_name,
            image_url=None,
            tags=["nepse", "financials", "quarterly", symbol.lower()],
            raw_data={
                "scraper": "NepseCompanyScraper",
                "record_type": "financial_report",
                "application_id": item.get("id"),
                "symbol": symbol,
                "security_id": security_id,
                "quarter": quarter_name,
                "report_type": report_type,
                "fiscal_year": fy_name,
                "eps": report.get("epsValue"),
                "pe": report.get("peValue"),
                "net_worth_per_share": report.get("netWorthPerShare"),
                "paid_up_capital": report.get("paidUpCapital"),
                "profit_amount": report.get("profitAmount"),
                "document_urls": _doc_urls(docs),
            },
            status="scraped",
        )

        return ScrapeResult(article=article, typed=typed)

    # ── Corporate action parser ───────────────────────────────────────────────

    def _parse_corporate_action(self, item: dict, company: dict) -> ScrapeResult:
        symbol        = company["symbol"]
        security_id   = company["id"]
        security_name = company.get("securityName", symbol)
        status        = item.get("activeStatus", "")
        fy            = item.get("fiscalYear", "")

        # ── Typed schema ──────────────────────────────────────────────────────
        typed = CorporateActionCreate(
            symbol=symbol,
            security_id=security_id,
            security_name=security_name,
            active_status=status or None,
            fiscal_year=fy or None,
            bonus_percentage=_to_decimal(item.get("bonusPercentage")),
            ratio_num=item.get("ratioNum"),
            ratio_den=item.get("ratioDen"),
            right_percentage=_to_decimal(item.get("rightPercentage")),
            right_amount_per_share=_to_decimal(item.get("rightAmountPerShare")),
            cash_dividend=_to_decimal(item.get("cashDividend")),
            submitted_date=_parse_dt(item.get("submittedDate")),
            file_path=item.get("filePath") or None,
            document_id=item.get("documentId"),
            sd_id=item.get("sdId"),
        )

        # ── ScrapedArticle ────────────────────────────────────────────────────
        parts = []
        if item.get("bonusPercentage"):
            parts.append(f"Bonus: {item['bonusPercentage']}%")
        if item.get("rightPercentage"):
            parts.append(f"Rights: {item['rightPercentage']}% @ Rs {item.get('rightAmountPerShare', '')}")
        if item.get("cashDividend"):
            parts.append(f"Cash Dividend: {item['cashDividend']}")
        if item.get("ratioNum") and item.get("ratioDen"):
            parts.append(f"Ratio: {item['ratioNum']}:{item['ratioDen']}")

        title = f"{status.replace('_', ' ').title()} FY{fy} [{symbol}]"

        article = ScrapedArticle(
            source_id=self.source_id,
            source_name=self.source_name,
            source_type="stock_exchange",
            original_url=_build_file_url(item.get("filePath")),
            title=title,
            summary=", ".join(parts) or status or None,
            content=(f"Symbol: {symbol}\nFiscal Year: {fy}\n" + "\n".join(parts)) if parts else None,
            language_code="en",
            published_at=_parse_dt(item.get("submittedDate")),
            author=security_name,
            image_url=None,
            tags=["nepse", "corporate-action", symbol.lower(), status.lower()],
            raw_data={
                "scraper": "NepseCompanyScraper",
                "record_type": "corporate_action",
                "symbol": symbol,
                "security_id": security_id,
                "sd_id": item.get("sdId"),
                "active_status": status,
                "fiscal_year": fy,
                "bonus_percentage": item.get("bonusPercentage"),
                "right_percentage": item.get("rightPercentage"),
                "right_amount_per_share": item.get("rightAmountPerShare"),
                "cash_dividend": item.get("cashDividend"),
                "ratio_num": item.get("ratioNum"),
                "ratio_den": item.get("ratioDen"),
            },
            status="scraped",
        )

        return ScrapeResult(article=article, typed=typed)