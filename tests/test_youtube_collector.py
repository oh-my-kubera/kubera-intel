"""Tests for YouTube Data API collector."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from intel.core.collectors.youtube import YouTubeCollector

YOUTUBE_RESPONSE = {
    "items": [
        {
            "id": {"videoId": "abc123"},
            "snippet": {
                "title": "삼성전자 실적 분석",
                "description": "2026년 1분기 실적 리뷰",
                "channelTitle": "투자채널",
                "publishedAt": "2026-02-23T09:00:00Z",
            },
        },
        {
            "id": {"videoId": "def456"},
            "snippet": {
                "title": "반도체 시장 전망",
                "description": "글로벌 반도체 시장 분석",
                "channelTitle": "경제TV",
                "publishedAt": "2026-02-22T15:00:00Z",
            },
        },
    ]
}


class TestYouTubeCollector:
    def test_collect_success(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = YOUTUBE_RESPONSE

        with patch("intel.core.collectors.youtube.httpx.get", return_value=mock_response) as mock_get:
            collector = YouTubeCollector(api_key="test-key")
            items = collector.collect(query="삼성전자")

        assert len(items) == 2
        assert items[0].source == "youtube"
        assert items[0].title == "삼성전자 실적 분석"
        assert items[0].url == "https://www.youtube.com/watch?v=abc123"
        assert items[0].metadata["channel"] == "투자채널"
        assert items[0].metadata["video_id"] == "abc123"

        mock_get.assert_called_once()
        call_params = mock_get.call_args[1]["params"]
        assert call_params["q"] == "삼성전자"
        assert call_params["key"] == "test-key"

    def test_collect_http_error(self):
        mock_response = MagicMock()
        mock_response.status_code = 403

        with patch("intel.core.collectors.youtube.httpx.get", return_value=mock_response):
            collector = YouTubeCollector(api_key="test-key")
            items = collector.collect(query="삼성전자")

        assert items == []

    def test_collect_empty_results(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}

        with patch("intel.core.collectors.youtube.httpx.get", return_value=mock_response):
            collector = YouTubeCollector(api_key="test-key")
            items = collector.collect(query="삼성전자")

        assert items == []

    def test_collect_max_results_capped(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}

        with patch("intel.core.collectors.youtube.httpx.get", return_value=mock_response) as mock_get:
            collector = YouTubeCollector(api_key="test-key")
            collector.collect(query="test", max_results=100)

        call_params = mock_get.call_args[1]["params"]
        assert call_params["maxResults"] == 50  # capped at API max
