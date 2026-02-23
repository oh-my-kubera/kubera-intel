"""Tests for Gemini analyzer."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from intel.core.analyzer.gemini import GeminiAnalyzer, _parse_analysis
from intel.core.collectors import CollectedItem

SAMPLE_ITEMS = [
    CollectedItem(
        source="news",
        title="삼성전자 실적 호조",
        url="https://example.com/1",
        published="2026-02-23",
        content="삼성전자가 4분기 실적이 예상치를 상회했다.",
        stock_code="005930",
    ),
    CollectedItem(
        source="dart",
        title="분기보고서",
        url="https://dart.fss.or.kr/1",
        published="2026-02-23",
        content="분기보고서 (2025.09)",
        stock_code="005930",
    ),
]

SAMPLE_ANALYSIS_RESPONSE = """SUMMARY:
삼성전자의 4분기 실적이 예상치를 상회하며 긍정적인 신호를 보이고 있습니다.

SENTIMENT:
positive

KEY_POINTS:
- 4분기 매출이 전년 대비 15% 증가
- 반도체 부문 영업이익 회복
- 분기보고서 공시 완료"""


class TestParseAnalysis:
    def test_parses_structured_response(self):
        result = _parse_analysis(SAMPLE_ANALYSIS_RESPONSE, stock_code="005930")
        assert "예상치를 상회" in result.summary
        assert result.sentiment == "positive"
        assert len(result.key_points) == 3
        assert result.stock_code == "005930"

    def test_handles_minimal_response(self):
        result = _parse_analysis("Just some text without structure")
        assert result.summary == "Just some text without structure"
        assert result.sentiment == "neutral"
        assert result.key_points == []

    def test_handles_negative_sentiment(self):
        text = "SUMMARY:\nBad news.\n\nSENTIMENT:\nnegative\n\nKEY_POINTS:\n- Loss"
        result = _parse_analysis(text)
        assert result.sentiment == "negative"


class TestGeminiAnalyzer:
    @patch("intel.core.analyzer.gemini.genai.Client")
    def test_analyze_items(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = MagicMock(
            text=SAMPLE_ANALYSIS_RESPONSE
        )
        mock_client_cls.return_value = mock_client

        analyzer = GeminiAnalyzer(api_key="test-key")
        result = analyzer.analyze_items(SAMPLE_ITEMS, stock_name="삼성전자")

        assert result.sentiment == "positive"
        assert len(result.key_points) == 3
        mock_client.models.generate_content.assert_called_once()

    @patch("intel.core.analyzer.gemini.genai.Client")
    def test_analyze_empty_items(self, mock_client_cls):
        analyzer = GeminiAnalyzer(api_key="test-key")
        result = analyzer.analyze_items([])
        assert result.sentiment == "neutral"
        assert "No data" in result.summary

    @patch("intel.core.analyzer.gemini.genai.Client")
    def test_generate_daily_brief(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = MagicMock(
            text="# Daily Brief\nContent here"
        )
        mock_client_cls.return_value = mock_client

        analyzer = GeminiAnalyzer(api_key="test-key")
        result = analyzer.generate_daily_brief(SAMPLE_ITEMS)

        assert "Daily Brief" in result
        mock_client.models.generate_content.assert_called_once()

    @patch("intel.core.analyzer.gemini.genai.Client")
    def test_generate_daily_brief_empty(self, mock_client_cls):
        analyzer = GeminiAnalyzer(api_key="test-key")
        result = analyzer.generate_daily_brief([])
        assert "No data" in result
