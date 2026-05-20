from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.source import Source
from app.schemas.source import SourceCreate, SourceResponse


router = APIRouter(
    prefix="/sources",
    tags=["Sources"],
)


@router.post("/", response_model=SourceResponse)
def create_source(source_data: SourceCreate, db: Session = Depends(get_db)):
    existing_source = (
        db.query(Source)
        .filter(Source.source_id == source_data.source_id.lower())
        .first()
    )

    if existing_source:
        raise HTTPException(
            status_code=400,
            detail="Source with this source_id already exists",
        )

    source = Source(
        source_id=source_data.source_id.lower(),
        source_name=source_data.source_name,
        source_type=source_data.source_type,
        website=source_data.website,
        language_code=source_data.language_code,
        reliability_score=source_data.reliability_score,
        is_active=source_data.is_active,
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return source


@router.get("/", response_model=list[SourceResponse])
def list_sources(db: Session = Depends(get_db)):
    sources = db.query(Source).order_by(Source.source_name.asc()).all()
    return sources


@router.get("/{source_id}", response_model=SourceResponse)
def get_source(source_id: str, db: Session = Depends(get_db)):
    source = (
        db.query(Source)
        .filter(Source.source_id == source_id.lower())
        .first()
    )

    if not source:
        raise HTTPException(
            status_code=404,
            detail="Source not found",
        )

    return source