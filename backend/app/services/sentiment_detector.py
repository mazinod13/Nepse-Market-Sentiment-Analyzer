POSITIVE_KEYWORDS = {
    "dividend_announcement": {
        "keywords": ["dividend", "bonus share", "cash dividend", "लाभांश", "बोनस शेयर"],
        "impact_score": 18,
    },
    "strong_quarterly_result": {
        "keywords": ["profit increased", "net profit rose", "नाफा बढ्यो", "revenue increased"],
        "impact_score": 20,
    },
    "credit_rating_improvement": {
        "keywords": ["rating upgraded", "credit rating improved"],
        "impact_score": 12,
    },
    "new_project_completion": {
        "keywords": ["project completed", "commercial operation", "completed construction"],
        "impact_score": 18,
    },
}

NEGATIVE_KEYWORDS = {
    "weak_quarterly_result": {
        "keywords": ["profit declined", "loss increased", "नाफा घट्यो", "revenue declined"],
        "impact_score": -20,
    },
    "regulatory_action": {
        "keywords": ["fine", "penalty", "कारबाही", "जरिवाना", "suspended"],
        "impact_score": -22,
    },
    "governance_concern": {
        "keywords": ["governance issue", "audit concern", "विवाद", "board dispute"],
        "impact_score": -20,
    },
    "project_delay": {
        "keywords": ["project delayed", "delay in construction", "construction delayed"],
        "impact_score": -15,
    },
}


def detect_sentiment_events(title: str, content: str | None = None) -> list[dict]:
    text = f"{title} {content or ''}".lower()
    detected_events = []

    for event_type, rule in POSITIVE_KEYWORDS.items():
        for keyword in rule["keywords"]:
            if keyword.lower() in text:
                detected_events.append(
                    {
                        "event_type": event_type,
                        "sentiment": "positive",
                        "impact_score": rule["impact_score"],
                        "confidence": 0.85,
                        "evidence": f"Detected keyword: {keyword}",
                    }
                )
                break

    for event_type, rule in NEGATIVE_KEYWORDS.items():
        for keyword in rule["keywords"]:
            if keyword.lower() in text:
                detected_events.append(
                    {
                        "event_type": event_type,
                        "sentiment": "negative",
                        "impact_score": rule["impact_score"],
                        "confidence": 0.85,
                        "evidence": f"Detected keyword: {keyword}",
                    }
                )
                break

    if not detected_events:
        detected_events.append(
            {
                "event_type": "neutral_news",
                "sentiment": "neutral",
                "impact_score": 0,
                "confidence": 0.60,
                "evidence": "No strong sentiment keyword detected",
            }
        )

    return detected_events