"""YouTube Data API v3 collector."""

from __future__ import annotations

import logging

import httpx

from intel.core.collectors import CollectedItem

logger = logging.getLogger(__name__)


class YouTubeCollector:
    BASE_URL = "https://www.googleapis.com/youtube/v3/search"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def collect(
        self,
        query: str,
        max_results: int = 10,
    ) -> list[CollectedItem]:
        """Search YouTube for financial videos matching query."""
        params = {
            "key": self.api_key,
            "q": query,
            "part": "snippet",
            "type": "video",
            "maxResults": min(max_results, 50),
            "order": "date",
            "relevanceLanguage": "ko",
        }

        logger.debug("YouTube search: query=%s, max=%d", query, max_results)

        response = httpx.get(self.BASE_URL, params=params, timeout=10.0)
        if response.status_code != 200:
            logger.error("YouTube API returned HTTP %d", response.status_code)
            return []

        data = response.json()
        items = []
        for entry in data.get("items", []):
            snippet = entry.get("snippet", {})
            video_id = entry.get("id", {}).get("videoId", "")
            items.append(
                CollectedItem(
                    source="youtube",
                    title=snippet.get("title", ""),
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    published=snippet.get("publishedAt", ""),
                    content=snippet.get("description", ""),
                    metadata={
                        "channel": snippet.get("channelTitle", ""),
                        "video_id": video_id,
                    },
                )
            )

        logger.info("YouTube collected %d videos for query=%s", len(items), query)
        return items
