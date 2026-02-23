"""Tests for daily reporter."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from intel.core.collectors import CollectedItem
from intel.core.reporter.daily import DailyReporter

SAMPLE_ITEMS = [
    CollectedItem(
        source="dart",
        title="분기보고서",
        url="https://dart.fss.or.kr/1",
        published="2026-02-23",
        stock_code="005930",
        metadata={"corp_name": "삼성전자"},
    ),
    CollectedItem(
        source="news",
        title="삼성전자 실적 호조",
        url="https://example.com/1",
        published="2026-02-23",
    ),
]


class TestDailyReporter:
    def test_generate_saves_markdown(self, intel_dir):
        mock_analyzer = MagicMock()
        mock_analyzer.generate_daily_brief.return_value = "## 주요 요약\n- 시장이 좋습니다"

        reporter = DailyReporter(analyzer=mock_analyzer)
        path = reporter.generate(items=SAMPLE_ITEMS)

        assert path.exists()
        assert path.suffix == ".md"
        content = path.read_text(encoding="utf-8")
        assert "일일 시장 리포트" in content
        assert "주요 요약" in content
        assert "삼성전자" in content
        mock_analyzer.generate_daily_brief.assert_called_once()

    def test_generate_market_close(self, intel_dir):
        mock_analyzer = MagicMock()
        mock_analyzer.generate_daily_brief.return_value = "Close report"

        reporter = DailyReporter(analyzer=mock_analyzer)
        path = reporter.generate(items=SAMPLE_ITEMS, market_close=True)

        assert "-close" in path.name
        content = path.read_text(encoding="utf-8")
        assert "장 마감" in content
