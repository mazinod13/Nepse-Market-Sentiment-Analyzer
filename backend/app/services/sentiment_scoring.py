def get_sentiment_label(score: int) -> str:
    if score >= 80:
        return "Very positive sentiment"
    if score >= 60:
        return "Positive sentiment"
    if score >= 40:
        return "Neutral sentiment"
    if score >= 20:
        return "Negative sentiment"
    return "Very negative sentiment"


def calculate_sentiment_score(events: list, base_score: int = 50) -> dict:
    total_impact = sum(event.impact_score for event in events)

    final_score = base_score + total_impact
    final_score = max(0, min(100, final_score))

    if events:
        average_confidence = sum(float(event.confidence or 0) for event in events) / len(events)
    else:
        average_confidence = 0.50

    label = get_sentiment_label(final_score)

    explanation = {
        "base_score": base_score,
        "total_impact": total_impact,
        "events": [
            {
                "event_type": event.event_type,
                "sentiment": event.sentiment,
                "impact_score": event.impact_score,
                "confidence": float(event.confidence or 0),
                "evidence": event.evidence,
            }
            for event in events
        ],
        "reason": f"Score calculated from {len(events)} sentiment event(s).",
    }

    return {
        "score": final_score,
        "label": label,
        "confidence": round(average_confidence, 4),
        "explanation": explanation,
    }