import pytest
from unittest.mock import patch, MagicMock
from app.data.news import fetch_rss_headlines, NewsItem


@pytest.mark.asyncio
async def test_fetch_rss_returns_list_of_news_items():
    mock_feed = MagicMock()
    mock_feed.entries = [
        MagicMock(title="RELIANCE Q3 profit up 12%", summary="Details...",
                  link="https://et.com/1", published="Mon, 01 Jan 2024 09:00:00 +0000"),
    ]
    with patch("app.data.news.feedparser.parse", return_value=mock_feed):
        items = await fetch_rss_headlines("RELIANCE")
    assert len(items) >= 1
    assert isinstance(items[0], NewsItem)
    assert items[0].title != ""


def test_news_item_fields():
    item = NewsItem(title="Test", summary="Sum", url="https://x.com", source="ET")
    assert item.title == "Test"
    assert item.source == "ET"
