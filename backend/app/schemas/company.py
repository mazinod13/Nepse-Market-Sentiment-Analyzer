from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CompanyBase(BaseModel):
    symbol: str
    company_name: str
    nepali_name: Optional[str] = None
    sector: Optional[str] = None
    instrument: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    status: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True