from app.models.company import Company


def match_article_to_companies(article, companies: list[Company]) -> list[dict]:
    text = f"{article.title or ''} {article.summary or ''} {article.content or ''}".lower()

    matches = []

    for company in companies:
        symbol = company.symbol.lower()
        company_name = company.company_name.lower()

        if symbol in text:
            matches.append(
                {
                    "company_symbol": company.symbol,
                    "match_type": "symbol",
                    "confidence": 0.98,
                }
            )
            continue

        if company_name in text:
            matches.append(
                {
                    "company_symbol": company.symbol,
                    "match_type": "company_name",
                    "confidence": 0.95,
                }
            )

    return matches