"""Tests for Naver News collector."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from intel.core.collectors.news import NaverNewsCollector, _parse_pub_date, _strip_html

SAMPLE_NEWS_RESPONSE = {
    "lastBuildDate": "Mon, 23 Feb 2026 12:00:00 +0900",
    "total": 100,
    "start": 1,
    "display": 2,
    "items": [
        {
            "title": "<b>삼성전자</b> 실적 호조",
            "originallink": "https://example.com/news/1",
            "link": "https://n.news.naver.com/1",
            "description": "<b>삼성전자</b>가 4분기 실적이 예상치를 상회했다.",
            "pubDate": "Mon, 23 Feb 2026 09:00:00 +0900",
        },
        {
            "title": "반도체 업황 &amp; 전망",
            "originallink": "",
            "link": "https://n.news.naver.com/2",
            "description": "반도체 업황이 &quot;회복&quot; 기조",
            "pubDate": "Mon, 23 Feb 2026 08:00:00 +0900",
        },
    ],
}


class TestNaverNewsCollector:
    @patch("intel.core.collectors.news.httpx.get")
    def test_collect_success(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = SAMPLE_NEWS_RESPONSE
        mock_get.return_value = mock_resp

        collector = NaverNewsCollector(client_id="cid", client_secret="csec")
        items = collector.collect(query="삼성전자")

        assert len(items) == 2
        assert items[0].source == "news"
        assert items[0].title == "삼성전자 실적 호조"  # HTML stripped
        assert items[0].url == "https://example.com/news/1"
        assert items[0].metadata["query"] == "삼성전자"

    @patch("intel.core.collectors.news.httpx.get")
    def test_collect_uses_link_fallback(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = SAMPLE_NEWS_RESPONSE
        mock_get.return_value = mock_resp

        collector = NaverNewsCollector(client_id="cid", client_secret="csec")
        items = collector.collect(query="반도체")
        # Second item has empty originallink, should use link
        assert items[1].url == "https://n.news.naver.com/2"

    @patch("intel.core.collectors.news.httpx.get")
    def test_collect_http_error(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_get.return_value = mock_resp

        collector = NaverNewsCollector(client_id="cid", client_secret="csec")
        items = collector.collect(query="test")
        assert items == []

    @patch("intel.core.collectors.news.httpx.get")
    def test_collect_passes_headers(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"items": []}
        mock_get.return_value = mock_resp

        collector = NaverNewsCollector(client_id="my-id", client_secret="my-secret")
        collector.collect(query="test")

        call_kwargs = mock_get.call_args
        headers = call_kwargs.kwargs.get("headers") or call_kwargs[1].get("headers")
        assert headers["X-Naver-Client-Id"] == "my-id"
        assert headers["X-Naver-Client-Secret"] == "my-secret"


class TestStripHtml:
    def test_removes_tags(self):
        assert _strip_html("<b>test</b>") == "test"

    def test_decodes_entities(self):
        assert _strip_html("a &amp; b &quot;c&quot;") == 'a & b "c"'

    def test_plain_text_unchanged(self):
        assert _strip_html("hello world") == "hello world"


class TestParsePubDate:
    def test_valid_rfc2822(self):
        result = _parse_pub_date("Mon, 23 Feb 2026 09:00:00 +0900")
        assert "2026-02-23" in result

    def test_invalid_returns_raw(self):
        assert _parse_pub_date("not a date") == "not a date"
