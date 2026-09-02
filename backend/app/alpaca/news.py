from __future__ import annotations

from datetime import datetime, timedelta, timezone

from alpaca.data.requests import NewsRequest

from app.alpaca.client import get_news_client
from app.models.prediction import Citation


def get_recent_news(symbol: str, *, lookback_days: int = 5, limit: int = 8) -> list[Citation]:
    """Fetch recent Alpaca news for `symbol` as evidence citations.

    Returns an empty list (never raises) if Alpaca news is unavailable -- callers
    must treat "no news" as a valid, low-information state rather than an error.
    """
    client = get_news_client()
    request = NewsRequest(
        symbols=symbol,
        start=datetime.now(timezone.utc) - timedelta(days=lookback_days),
        limit=limit,
    )
    news_set = client.get_news(request)
    articles = news_set.data.get("news", [])
    return [
        Citation(
            headline=article.headline,
            source=article.source,
            url=article.url,
            published_at=article.created_at,
        )
        for article in articles
    ]
