import json
import sys
from pathlib import Path

# Allow running this script from backend/ using:
# python scripts/seed_active_companies.py
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BACKEND_DIR))

from app.db.database import SessionLocal
from app.models.company import Company
from app.models.company_alias import CompanyAlias


SEED_DIR = BACKEND_DIR / "app" / "seeds"
COMPANIES_FILE = SEED_DIR / "companies_seed.json"
ALIASES_FILE = SEED_DIR / "company_aliases_seed.json"


def load_json_file(file_path: Path):
    if not file_path.exists():
        raise FileNotFoundError(f"Seed file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def normalize_website(website: str | None) -> str | None:
    if not website:
        return None

    website = website.strip()

    if not website:
        return None

    if website.startswith("http://") or website.startswith("https://"):
        return website

    return f"https://{website}"


def seed_companies(db, companies: list[dict]):
    created_count = 0
    updated_count = 0

    for item in companies:
        symbol = item["symbol"].upper().strip()

        existing_company = (
            db.query(Company)
            .filter(Company.symbol == symbol)
            .first()
        )

        company_payload = {
            "symbol": symbol,
            "company_name": item["company_name"],
            "nepali_name": item.get("nepali_name"),
            "sector": item.get("sector"),
            "instrument": item.get("instrument"),
            "email": item.get("email"),
            "website": normalize_website(item.get("website")),
            "status": item.get("status", "active"),
        }

        if existing_company:
            existing_company.company_name = company_payload["company_name"]
            existing_company.nepali_name = company_payload["nepali_name"]
            existing_company.sector = company_payload["sector"]
            existing_company.instrument = company_payload["instrument"]
            existing_company.email = company_payload["email"]
            existing_company.website = company_payload["website"]
            existing_company.status = company_payload["status"]

            updated_count += 1
        else:
            company = Company(**company_payload)
            db.add(company)
            created_count += 1

    db.commit()

    return created_count, updated_count


def seed_aliases(db, aliases: list[dict]):
    created_count = 0
    skipped_count = 0

    for item in aliases:
        company_symbol = item["company_symbol"].upper().strip()
        alias = item["alias"].strip()

        if not alias:
            skipped_count += 1
            continue

        company = (
            db.query(Company)
            .filter(Company.symbol == company_symbol)
            .first()
        )

        if not company:
            skipped_count += 1
            continue

        existing_alias = (
            db.query(CompanyAlias)
            .filter(
                CompanyAlias.company_symbol == company_symbol,
                CompanyAlias.alias == alias,
            )
            .first()
        )

        if existing_alias:
            skipped_count += 1
            continue

        company_alias = CompanyAlias(
            company_symbol=company_symbol,
            alias=alias,
            language_code=item.get("language_code"),
            alias_type=item.get("alias_type"),
        )

        db.add(company_alias)
        created_count += 1

    db.commit()

    return created_count, skipped_count


def main():
    print("Loading seed files...")

    companies = load_json_file(COMPANIES_FILE)
    aliases = load_json_file(ALIASES_FILE)

    print(f"Companies found: {len(companies)}")
    print(f"Aliases found: {len(aliases)}")

    db = SessionLocal()

    try:
        companies_created, companies_updated = seed_companies(db, companies)
        aliases_created, aliases_skipped = seed_aliases(db, aliases)

        print("\nSeed completed successfully.")
        print(f"Companies created: {companies_created}")
        print(f"Companies updated: {companies_updated}")
        print(f"Aliases created: {aliases_created}")
        print(f"Aliases skipped: {aliases_skipped}")

    except Exception as error:
        db.rollback()
        print("\nSeed failed.")
        print(str(error))
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()