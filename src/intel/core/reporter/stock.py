"""Stock deep dive report generator."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from intel.core.analyzer.gemini import GeminiAnalyzer
from intel.core.collectors import CollectedItem
from intel.core.config import reports_dir
from intel.core.reporter.templates import stock_report_template


class StockReporter:
    def __init__(self, analyzer: GeminiAnalyzer):
        self.analyzer = analyzer

    def generate(
        self,
        stock_code: str,
        stock_name: str,
        items: list[CollectedItem],
    ) -> Path:
        """Generate stock deep dive report and save as markdown."""
        today = date.today().isoformat()

        analysis = self.analyzer.analyze_items(items, stock_name=stock_name)

        content = stock_report_template(
            code=stock_code,
            name=stock_name,
            date=today,
            summary=analysis.summary,
            sentiment=analysis.sentiment,
            key_points=analysis.key_points,
            items=items,
        )

        out_path = reports_dir() / f"stock-{stock_code}-{today}.md"
        out_path.write_text(content, encoding="utf-8")
        return out_path
