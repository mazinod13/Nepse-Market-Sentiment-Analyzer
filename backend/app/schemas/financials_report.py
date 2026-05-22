from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


# ── Sub-schemas ───────────────────────────────────────────────────────────────

class QuarterMasterSchema(BaseModel):
    id: Optional[int] = None
    quarter_name: Optional[str] = None      # "First Quarter", "Third Quarter", etc.


class ReportTypeMasterSchema(BaseModel):
    id: Optional[int] = None
    report_name: Optional[str] = None       # "Quarterly Report", "Annual Report", etc.


class FinancialYearSchema(BaseModel):
    id: Optional[int] = None
    fy_name: Optional[str] = None           # "2025-2026"
    fy_name_nepali: Optional[str] = None    # "2082-2083"
    from_year: Optional[date] = None
    to_year: Optional[date] = None


class FinancialDocumentSchema(BaseModel):
    id: Optional[int] = None
    file_path: Optional[str] = None
    encrypted_id: Optional[str] = None
    submitted_date: Optional[date] = None
    document_type: Optional[int] = None


# ── Base ──────────────────────────────────────────────────────────────────────

class FinancialReportBase(BaseModel):
    # Which company
    symbol: str
    security_id: int
    security_name: Optional[str] = None

    # Report classification (flattened for easy querying/filtering)
    quarter_id: Optional[int] = None
    quarter_name: Optional[str] = None      # "Third Quarter"
    report_type_id: Optional[int] = None
    report_type_name: Optional[str] = None  # "Quarterly Report"

    # Fiscal year (flattened)
    fiscal_year_id: Optional[int] = None
    fiscal_year: Optional[str] = None       # "2025-2026"
    fiscal_year_nepali: Optional[str] = None

    # Core financial metrics
    eps: Optional[Decimal] = None           # Earnings per share
    pe: Optional[Decimal] = None            # Price-to-earnings ratio
    net_worth_per_share: Optional[Decimal] = None
    paid_up_capital: Optional[Decimal] = None
    profit_amount: Optional[Decimal] = None

    remarks: Optional[str] = None
    published_at: Optional[datetime] = None

    # Nested detail
    quarter_master: Optional[QuarterMasterSchema] = None
    report_type_master: Optional[ReportTypeMasterSchema] = None
    financial_year: Optional[FinancialYearSchema] = None
    documents: Optional[list[FinancialDocumentSchema]] = []

    # Raw application metadata
    application_id: Optional[int] = None
    fiscal_report_id: Optional[int] = None
    application_status: Optional[int] = None


# ── Create / Update ───────────────────────────────────────────────────────────

class FinancialReportCreate(FinancialReportBase):
    pass


class FinancialReportUpdate(BaseModel):
    """Partial update — all fields optional."""
    quarter_name: Optional[str] = None
    report_type_name: Optional[str] = None
    fiscal_year: Optional[str] = None
    fiscal_year_nepali: Optional[str] = None
    eps: Optional[Decimal] = None
    pe: Optional[Decimal] = None
    net_worth_per_share: Optional[Decimal] = None
    paid_up_capital: Optional[Decimal] = None
    profit_amount: Optional[Decimal] = None
    remarks: Optional[str] = None
    published_at: Optional[datetime] = None
    documents: Optional[list[FinancialDocumentSchema]] = None


# ── Response ──────────────────────────────────────────────────────────────────

class FinancialReportResponse(FinancialReportBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True