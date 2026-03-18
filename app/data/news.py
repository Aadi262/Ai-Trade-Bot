from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import feedparser
import structlog

logger = structlog.get_logger(__name__)

ET_RSS = "https://economictimes.indiatimes.com/markets/stocks/rss.cms"
MC_RSS = "https://www.moneycontrol.com/rss/marketsnews.xml"


@dataclass
class NewsItem:
    title: str
    summary: str
    url: str
    source: str
    published_at: datetime | None = None


async def fetch_rss_headlines(symbol: str, max_items: int = 20) -> list[NewsItem]:
    items: list[NewsItem] = []
    # Strip exchange suffix so "RELIANCE.NS" → "RELIANCE" for text matching
    ticker = symbol.replace(".NS", "").replace(".BO", "").upper()

    for url, source in [(ET_RSS, "ET"), (MC_RSS, "MC")]:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_items]:
                # feedparser entry objects expose fields as attributes, not dict keys.
                # Using getattr with a default is the correct approach for both real
                # feedparser entries and MagicMock test doubles.
                title: str = getattr(entry, "title", "") or ""
                summary: str = getattr(entry, "summary", "") or ""
                link: str = getattr(entry, "link", "") or ""

                text = (title + " " + summary).upper()
                if ticker in text:
                    items.append(
                        NewsItem(
                            title=title,
                            summary=summary,
                            url=link,
                            source=source,
                        )
                    )
        except Exception as exc:
            logger.warning("rss_fetch_failed", source=source, error=str(exc))

    logger.info("news_fetched", symbol=symbol, count=len(items))
    return items
