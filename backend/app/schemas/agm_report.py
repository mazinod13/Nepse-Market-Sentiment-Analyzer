from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


# ── Sub-schemas (nested objects from the API) ─────────────────────────────────

class AgmNoticeSchema(BaseModel):
    id: Optional[int] = None
    agm_type: Optional[str] = None          # "AGM", "EGM", etc.
    agm_date: Optional[date] = None
    agm_no: Optional[int] = None
    book_close_date: Optional[date] = None
    cash_dividend: Optional[Decimal] = None
    bonus_share: Optional[Decimal] = None   # percentage e.g. 5.0 → 5%
    agenda: Optional[str] = None
    venue: Optional[str] = None
    remarks: Optional[str] = None


class AgmDocumentSchema(BaseModel):
    id: Optional[int] = None
    file_path: Optional[str] = None
    encrypted_id: Optional[str] = None
    submitted_date: Optional[date] = None
    document_type: Optional[int] = None


# ── Base ──────────────────────────────────────────────────────────────────────

class AgmReportBase(BaseModel):
    # Which company
    symbol: str
    security_id: int
    security_name: Optional[str] = None

    # News/headline fields
    news_headline: Optional[str] = None
    news_body: Optional[str] = None
    news_type: Optional[str] = None         # "Annual General Meeting"
    news_source: Optional[str] = None
    language_code: Optional[str] = "en"

    # AGM specifics (flattened for easy querying)
    agm_type: Optional[str] = None
    agm_no: Optional[int] = None
    agm_date: Optional[date] = None
    book_close_date: Optional[date] = None
    cash_dividend: Optional[Decimal] = None
    bonus_share: Optional[Decimal] = None
    venue: Optional[str] = None
    agenda: Optional[str] = None

    # Dates
    published_at: Optional[datetime] = None
    expiry_date: Optional[date] = None

    # Nested detail (stored as JSON in DB / passed through API)
    agm_notice: Optional[AgmNoticeSchema] = None
    documents: Optional[list[AgmDocumentSchema]] = []

    # Raw application metadata
    application_id: Optional[int] = None
    application_status: Optional[int] = None


# ── Create / Update ───────────────────────────────────────────────────────────

class AgmReportCreate(AgmReportBase):
    pass


class AgmReportUpdate(BaseModel):
    """Partial update — all fields optional."""
    news_headline: Optional[str] = None
    news_body: Optional[str] = None
    agm_type: Optional[str] = None
    agm_no: Optional[int] = None
    agm_date: Optional[date] = None
    book_close_date: Optional[date] = None
    cash_dividend: Optional[Decimal] = None
    bonus_share: Optional[Decimal] = None
    venue: Optional[str] = None
    agenda: Optional[str] = None
    published_at: Optional[datetime] = None
    expiry_date: Optional[date] = None
    agm_notice: Optional[AgmNoticeSchema] = None
    documents: Optional[list[AgmDocumentSchema]] = None


# ── Response ──────────────────────────────────────────────────────────────────

class AgmReportResponse(AgmReportBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True