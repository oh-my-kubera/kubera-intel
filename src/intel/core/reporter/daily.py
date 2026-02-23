"""Daily market report generator."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from intel.core.analyzer.gemini import GeminiAnalyzer
from intel.core.collectors import CollectedItem
from intel.core.config import reports_dir
from intel.core.reporter.templates import daily_report_template


class DailyReporter:
    def __init__(self, analyzer: GeminiAnalyzer):
        self.analyzer = analyzer

    def generate(
        self,
        items: list[CollectedItem],
        market_close: bool = False,
    ) -> Path:
        """Generate daily report and save as markdown."""
        today = date.today().isoformat()

        brief = self.analyzer.generate_daily_brief(items)

        dart_items = [i for i in items if i.source == "dart"]
        news_items = [i for i in items if i.source == "news"]

        content = daily_report_template(
            date=today,
            brief=brief,
            dart_items=dart_items,
            news_items=news_items,
            market_close=market_close,
        )

        suffix = "-close" if market_close else ""
        out_path = reports_dir() / f"daily-{today}{suffix}.md"
        out_path.write_text(content, encoding="utf-8")
        return out_path
