from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyResponse


router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


@router.post("/", response_model=CompanyResponse)
def create_company(company_data: CompanyCreate, db: Session = Depends(get_db)):
    existing_company = (
        db.query(Company)
        .filter(Company.symbol == company_data.symbol.upper())
        .first()
    )

    if existing_company:
        raise HTTPException(
            status_code=400,
            detail="Company with this symbol already exists",
        )

    company = Company(
        symbol=company_data.symbol.upper(),
        company_name=company_data.company_name,
        sector=company_data.sector,
        instrument=company_data.instrument,
        email=company_data.email,
        website=company_data.website,
        status=company_data.status,
    )

    db.add(company)
    db.commit()
    db.refresh(company)

    return company


@router.get("/", response_model=list[CompanyResponse])
def list_companies(db: Session = Depends(get_db)):
    companies = db.query(Company).order_by(Company.symbol.asc()).all()
    return companies


@router.get("/{symbol}", response_model=CompanyResponse)
def get_company(symbol: str, db: Session = Depends(get_db)):
    company = (
        db.query(Company)
        .filter(Company.symbol == symbol.upper())
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )

    return company