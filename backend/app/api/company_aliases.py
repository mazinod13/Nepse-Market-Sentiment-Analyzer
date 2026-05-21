from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.company import Company
from app.models.company_alias import CompanyAlias
from app.schemas.company_alias import CompanyAliasCreate, CompanyAliasResponse


router = APIRouter(
    prefix="/company-aliases",
    tags=["Company Aliases"],
)


@router.post("/", response_model=CompanyAliasResponse)
def create_company_alias(
    alias_data: CompanyAliasCreate,
    db: Session = Depends(get_db),
):
    symbol = alias_data.company_symbol.upper()

    company = (
        db.query(Company)
        .filter(Company.symbol == symbol)
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )

    existing_alias = (
        db.query(CompanyAlias)
        .filter(
            CompanyAlias.company_symbol == symbol,
            CompanyAlias.alias == alias_data.alias,
        )
        .first()
    )

    if existing_alias:
        raise HTTPException(
            status_code=400,
            detail="Alias already exists for this company",
        )

    company_alias = CompanyAlias(
        company_symbol=symbol,
        alias=alias_data.alias,
        language_code=alias_data.language_code,
        alias_type=alias_data.alias_type,
    )

    db.add(company_alias)
    db.commit()
    db.refresh(company_alias)

    return company_alias


@router.get("/", response_model=list[CompanyAliasResponse])
def list_company_aliases(db: Session = Depends(get_db)):
    aliases = (
        db.query(CompanyAlias)
        .order_by(CompanyAlias.company_symbol.asc(), CompanyAlias.alias.asc())
        .all()
    )

    return aliases


@router.get("/{symbol}", response_model=list[CompanyAliasResponse])
def get_company_aliases(symbol: str, db: Session = Depends(get_db)):
    aliases = (
        db.query(CompanyAlias)
        .filter(CompanyAlias.company_symbol == symbol.upper())
        .order_by(CompanyAlias.alias.asc())
        .all()
    )

    return aliases