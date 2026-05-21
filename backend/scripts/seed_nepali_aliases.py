import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BACKEND_DIR))

from app.db.database import SessionLocal
from app.models.company import Company
from app.models.company_alias import CompanyAlias

ALIASES_FILE = BACKEND_DIR / "app" / "seeds" / "company_aliases_nepali_generated.json"


def main():
    aliases = json.load(open(ALIASES_FILE, "r", encoding="utf-8"))
    db = SessionLocal()
    created = 0
    skipped = 0
    try:
        for item in aliases:
            symbol = item["company_symbol"].upper().strip()
            alias = item["alias"].strip()
            if not alias:
                skipped += 1
                continue
            company = db.query(Company).filter(Company.symbol == symbol).first()
            if not company:
                skipped += 1
                continue
            exists = db.query(CompanyAlias).filter(
                CompanyAlias.company_symbol == symbol,
                CompanyAlias.alias == alias,
            ).first()
            if exists:
                skipped += 1
                continue
            db.add(CompanyAlias(
                company_symbol=symbol,
                alias=alias,
                language_code=item.get("language_code", "ne"),
                alias_type=item.get("alias_type", "ne_machine"),
            ))
            created += 1
        db.commit()
        print("Nepali alias seed completed successfully.")
        print(f"Aliases created: {created}")
        print(f"Aliases skipped: {skipped}")
    except Exception as error:
        db.rollback()
        print("Nepali alias seed failed.")
        print(error)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
