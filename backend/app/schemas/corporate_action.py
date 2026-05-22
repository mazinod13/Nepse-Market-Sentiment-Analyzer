from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, model_validator


# ── Action type literal ───────────────────────────────────────────────────────

ActionStatus = Literal[
    "BONUS_APPROVED",
    "BONUS_PENDING",
    "RIGHTS_APPROVED",
    "RIGHTS_PENDING",
    "CASH_DIVIDEND_APPROVED",
    "CASH_DIVIDEND_PENDING",
]


# ── Base ──────────────────────────────────────────────────────────────────────

class CorporateActionBase(BaseModel):
    # Which company
    symbol: str
    security_id: int
    security_name: Optional[str] = None

    # Action classification
    active_status: Optional[str] = None     # raw value e.g. "BONUS_APPROVED"
    fiscal_year: Optional[str] = None       # Nepali FY e.g. "2081-2082"

    # Bonus share fields
    bonus_percentage: Optional[Decimal] = None  # e.g. 5.0 → 5%
    ratio_num: Optional[int] = None             # e.g. 1  (1:20 → 5%)
    ratio_den: Optional[int] = None             # e.g. 20

    # Rights issue fields
    right_percentage: Optional[Decimal] = None  # e.g. 40.0 → 40%
    right_amount_per_share: Optional[Decimal] = None  # issue price e.g. 100.0

    # Cash dividend
    cash_dividend: Optional[Decimal] = None

    # Dates & references
    submitted_date: Optional[datetime] = None
    file_path: Optional[str] = None
    document_id: Optional[int] = None
    sd_id: Optional[int] = None             # NEPSE internal settlement/distribution ID

    # Derived convenience field (populated by validator)
    action_type: Optional[str] = None       # "bonus" | "rights" | "cash_dividend" | "unknown"

    @model_validator(mode="after")
    def derive_action_type(self) -> "CorporateActionBase":
        status = (self.active_status or "").upper()
        if "BONUS" in status:
            self.action_type = "bonus"
        elif "RIGHTS" in status:
            self.action_type = "rights"
        elif "CASH" in status or "DIVIDEND" in status:
            self.action_type = "cash_dividend"
        else:
            self.action_type = "unknown"
        return self


# ── Create / Update ───────────────────────────────────────────────────────────

class CorporateActionCreate(CorporateActionBase):
    pass


class CorporateActionUpdate(BaseModel):
    """Partial update — all fields optional."""
    active_status: Optional[str] = None
    fiscal_year: Optional[str] = None
    bonus_percentage: Optional[Decimal] = None
    ratio_num: Optional[int] = None
    ratio_den: Optional[int] = None
    right_percentage: Optional[Decimal] = None
    right_amount_per_share: Optional[Decimal] = None
    cash_dividend: Optional[Decimal] = None
    submitted_date: Optional[datetime] = None
    file_path: Optional[str] = None
    sd_id: Optional[int] = None


# ── Response ──────────────────────────────────────────────────────────────────

class CorporateActionResponse(CorporateActionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True