from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CompanyAliasBase(BaseModel):
    company_symbol: str
    alias: str
    language_code: Optional[str] = None
    alias_type: Optional[str] = None


class CompanyAliasCreate(CompanyAliasBase):
    pass


class CompanyAliasResponse(CompanyAliasBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True