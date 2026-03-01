"""Naver News Search API collector."""

from __future__ import annotations

import logging
import re
from email.utils import parsedate_to_datetime

import httpx

from intel.core.collectors import CollectedItem

logger = logging.getLogger(__name__)


class NaverNewsCollector:
    BASE_URL = "https://openapi.naver.com/v1/search/news.json"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    def collect(
        self,
        query: str,
        max_results: int = 20,
        sort: str = "date",
    ) -> list[CollectedItem]:
        """Search Naver news for a query."""
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
        }
        params = {
            "query": query,
            "display": min(max_results, 100),
            "sort": sort,
        }

        logger.debug("Naver news search: query=%s, max=%d", query, max_results)

        response = httpx.get(
            self.BASE_URL,
            headers=headers,
            params=params,
            timeout=10.0,
        )
        if response.status_code != 200:
            logger.error("Naver API returned HTTP %d", response.status_code)
            return []

        data = response.json()
        items = []
        for entry in data.get("items", []):
            published = _parse_pub_date(entry.get("pubDate", ""))
            items.append(
                CollectedItem(
                    source="news",
                    title=_strip_html(entry.get("title", "")),
                    url=entry.get("originallink") or entry.get("link", ""),
                    published=published,
                    content=_strip_html(entry.get("description", "")),
                    metadata={"query": query},
                )
            )
        logger.info("Naver news collected %d items for query=%s", len(items), query)
        return items


def _strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    return re.sub(r"<[^>]+>", "", text).replace("&quot;", '"').replace("&amp;", "&")


def _parse_pub_date(raw: str) -> str:
    """Parse RFC 2822 date to ISO format."""
    try:
        dt = parsedate_to_datetime(raw)
        return dt.isoformat()
    except Exception:
        return raw
