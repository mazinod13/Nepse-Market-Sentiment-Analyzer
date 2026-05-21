import re

from app.models.company import Company
from app.models.company_alias import CompanyAlias


def normalize_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").lower().strip()


def is_equity_company(company: Company) -> bool:
    return normalize_text(company.instrument) == "equity"


def contains_exact_token(text: str, token: str) -> bool:
    """
    Match exact token only.

    Example:
    - NABIL matches "NABIL announces dividend"
    - NABIL does NOT match "NABILD87 announces listing"
    """
    if not token:
        return False

    pattern = rf"(?<![A-Za-z0-9]){re.escape(token.lower())}(?![A-Za-z0-9])"
    return re.search(pattern, text.lower()) is not None


def contains_phrase(text: str, phrase: str) -> bool:
    phrase = normalize_text(phrase)

    if not phrase:
        return False

    pattern = rf"(?<![A-Za-z0-9]){re.escape(phrase)}(?![A-Za-z0-9])"
    return re.search(pattern, text) is not None


def match_article_to_companies(
    article,
    companies: list[Company],
    aliases: list[CompanyAlias] | None = None,
) -> list[dict]:
    text = normalize_text(
        f"{article.title or ''} {article.summary or ''} {article.content or ''}"
    )

    aliases = aliases or []

    aliases_by_symbol = {}
    for item in aliases:
        aliases_by_symbol.setdefault(item.company_symbol, []).append(item)

    # Step 1: exact symbol matching.
    # If article explicitly mentions a symbol like NABIL, return only that exact symbol.
    exact_symbol_matches = []

    for company in companies:
        symbol = company.symbol.upper().strip()

        if contains_exact_token(text, symbol):
            exact_symbol_matches.append(
                {
                    "company_symbol": symbol,
                    "match_type": "symbol",
                    "confidence": 0.99,
                }
            )

    if exact_symbol_matches:
        return exact_symbol_matches

    # Step 2: company name / alias matching.
    # For general names like "Nabil Bank", only match equity instruments.
    matches = []
    seen = set()

    for company in companies:
        if not is_equity_company(company):
            continue

        symbol = company.symbol.upper().strip()
        company_name = normalize_text(company.company_name)
        nepali_name = normalize_text(getattr(company, "nepali_name", None))

        if company_name and contains_phrase(text, company_name):
            matches.append(
                {
                    "company_symbol": symbol,
                    "match_type": "company_name",
                    "confidence": 0.95,
                }
            )
            seen.add(symbol)
            continue

        if nepali_name and contains_phrase(text, nepali_name):
            matches.append(
                {
                    "company_symbol": symbol,
                    "match_type": "nepali_name",
                    "confidence": 0.95,
                }
            )
            seen.add(symbol)
            continue

        for alias in aliases_by_symbol.get(symbol, []):
            alias_text = normalize_text(alias.alias)

            if not alias_text:
                continue

            # Symbol aliases already handled above.
            if alias.alias_type == "symbol":
                continue

            # Website aliases can be too broad, use lower confidence.
            if contains_phrase(text, alias_text):
                confidence = 0.90

                if alias.alias_type == "legal_name":
                    confidence = 0.95
                elif alias.alias_type == "short_name":
                    confidence = 0.90
                elif alias.alias_type == "nepali_generated":
                    confidence = 0.88
                elif alias.alias_type == "website_name":
                    confidence = 0.80

                matches.append(
                    {
                        "company_symbol": symbol,
                        "match_type": f"alias:{alias.alias_type or 'general'}",
                        "confidence": confidence,
                    }
                )
                seen.add(symbol)
                break

    unique_matches = []
    used_symbols = set()

    for match in matches:
        symbol = match["company_symbol"]

        if symbol in used_symbols:
            continue

        unique_matches.append(match)
        used_symbols.add(symbol)

    return unique_matches