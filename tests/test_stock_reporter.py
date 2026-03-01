"""Tests for stock deep dive reporter."""

from __future__ import annotations

from unittest.mock import MagicMock

from intel.core.analyzer.gemini import AnalysisResult
from intel.core.collectors import CollectedItem
from intel.core.reporter.stock import StockReporter

SAMPLE_ITEMS = [
    CollectedItem(
        source="dart",
        title="분기보고서",
        url="https://dart.fss.or.kr/1",
        published="2026-02-23",
        stock_code="005930",
    ),
    CollectedItem(
        source="news",
        title="삼성전자 실적 호조",
        url="https://example.com/1",
        published="2026-02-23",
        stock_code="005930",
    ),
]

MOCK_ANALYSIS = AnalysisResult(
    summary="삼성전자의 4분기 실적이 예상치를 상회했습니다.",
    sentiment="positive",
    key_points=["매출 15% 증가", "반도체 영업이익 회복"],
    stock_code="005930",
)


class TestStockReporter:
    def test_generate_saves_markdown(self, intel_dir):
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_items.return_value = MOCK_ANALYSIS

        reporter = StockReporter(analyzer=mock_analyzer)
        path = reporter.generate(
            stock_code="005930", stock_name="삼성전자", items=SAMPLE_ITEMS
        )

        assert path.exists()
        assert path.suffix == ".md"
        assert "stock-005930-" in path.name
        content = path.read_text(encoding="utf-8")
        assert "삼성전자 (005930)" in content
        assert "심층 분석" in content
        assert "예상치를 상회" in content
        assert "positive" in content
        assert "매출 15% 증가" in content
        mock_analyzer.analyze_items.assert_called_once_with(
            SAMPLE_ITEMS, stock_name="삼성전자"
        )

    def test_generate_includes_related_items(self, intel_dir):
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_items.return_value = MOCK_ANALYSIS

        reporter = StockReporter(analyzer=mock_analyzer)
        path = reporter.generate(
            stock_code="005930", stock_name="삼성전자", items=SAMPLE_ITEMS
        )

        content = path.read_text(encoding="utf-8")
        assert "관련 자료" in content
        assert "분기보고서" in content
        assert "실적 호조" in content

    def test_generate_empty_items(self, intel_dir):
        mock_analysis = AnalysisResult(
            summary="No data", sentiment="neutral", key_points=[]
        )
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_items.return_value = mock_analysis

        reporter = StockReporter(analyzer=mock_analyzer)
        path = reporter.generate(
            stock_code="000660", stock_name="SK하이닉스", items=[]
        )

        assert path.exists()
        assert "stock-000660-" in path.name
        content = path.read_text(encoding="utf-8")
        assert "SK하이닉스 (000660)" in content
        assert "neutral" in content

    def test_generate_file_naming(self, intel_dir):
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_items.return_value = MOCK_ANALYSIS

        reporter = StockReporter(analyzer=mock_analyzer)
        path = reporter.generate(
            stock_code="005930", stock_name="삼성전자", items=SAMPLE_ITEMS
        )

        assert path.parent.name == "reports"
        assert path.name.startswith("stock-005930-")
        assert path.name.endswith(".md")
