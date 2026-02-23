"""Tests for DART collector."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from intel.core.collectors.dart import DartCollector, _format_date

SAMPLE_DART_RESPONSE = {
    "status": "000",
    "message": "정상",
    "page_no": 1,
    "page_count": 10,
    "total_count": 2,
    "total_page": 1,
    "list": [
        {
            "corp_code": "00126380",
            "corp_name": "삼성전자",
            "stock_code": "005930",
            "corp_cls": "Y",
            "report_nm": "분기보고서 (2025.09)",
            "rcept_no": "20260220000001",
            "flr_nm": "삼성전자",
            "rcept_dt": "20260220",
            "rm": "",
        },
        {
            "corp_code": "00126380",
            "corp_name": "삼성전자",
            "stock_code": "005930",
            "corp_cls": "Y",
            "report_nm": "임원ㆍ주요주주특정증권등소유상황보고서",
            "rcept_no": "20260219000002",
            "flr_nm": "홍길동",
            "rcept_dt": "20260219",
            "rm": "",
        },
    ],
}


class TestDartCollector:
    @patch("intel.core.collectors.dart.httpx.get")
    def test_collect_success(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = SAMPLE_DART_RESPONSE
        mock_get.return_value = mock_resp

        collector = DartCollector(api_key="test-key")
        items = collector.collect(stock_code="005930")

        assert len(items) == 2
        assert items[0].source == "dart"
        assert items[0].title == "분기보고서 (2025.09)"
        assert items[0].stock_code == "005930"
        assert "rcpNo=20260220000001" in items[0].url
        assert items[0].metadata["corp_name"] == "삼성전자"

    @patch("intel.core.collectors.dart.httpx.get")
    def test_collect_no_data(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"status": "013", "message": "조회된 데이터가 없습니다."}
        mock_get.return_value = mock_resp

        collector = DartCollector(api_key="test-key")
        items = collector.collect(stock_code="999999")
        assert items == []

    @patch("intel.core.collectors.dart.httpx.get")
    def test_collect_http_error(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_get.return_value = mock_resp

        collector = DartCollector(api_key="test-key")
        items = collector.collect()
        assert items == []


class TestFormatDate:
    def test_valid_date(self):
        assert _format_date("20260223") == "2026-02-23"

    def test_invalid_date(self):
        assert _format_date("abc") == "abc"
