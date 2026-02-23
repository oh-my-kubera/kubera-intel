"""Gemini AI analyzer for summarization and sentiment analysis."""

from __future__ import annotations

from dataclasses import dataclass, field

from google import genai

from intel.core.collectors import CollectedItem


@dataclass
class AnalysisResult:
    summary: str
    sentiment: str  # "positive", "negative", "neutral"
    key_points: list[str] = field(default_factory=list)
    stock_code: str = ""


class GeminiAnalyzer:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model

    def analyze_items(
        self, items: list[CollectedItem], stock_name: str = ""
    ) -> AnalysisResult:
        """Summarize and analyze a batch of items about one stock."""
        if not items:
            return AnalysisResult(summary="No data available.", sentiment="neutral")

        items_text = "\n".join(
            f"- [{item.source}] {item.title}: {item.content[:200]}" for item in items
        )
        stock_label = stock_name or items[0].stock_code or "the stock"

        prompt = f"""Analyze the following financial news and disclosures about {stock_label}.
Respond in Korean. Use exactly this format:

SUMMARY:
(2-3 sentence summary of the overall situation)

SENTIMENT:
(exactly one of: positive, negative, neutral)

KEY_POINTS:
- (point 1)
- (point 2)
- (point 3)

Data:
{items_text}"""

        response = self.client.models.generate_content(model=self.model_name, contents=prompt)
        return _parse_analysis(response.text, stock_code=items[0].stock_code)

    def generate_daily_brief(self, items: list[CollectedItem]) -> str:
        """Generate a daily market brief from all collected items. Returns markdown."""
        if not items:
            return "No data collected today."

        dart_items = [i for i in items if i.source == "dart"]
        news_items = [i for i in items if i.source == "news"]

        items_text = ""
        if dart_items:
            items_text += "## DART Disclosures\n"
            items_text += "\n".join(
                f"- {i.metadata.get('corp_name', '')} | {i.title}" for i in dart_items[:30]
            )
            items_text += "\n\n"
        if news_items:
            items_text += "## News\n"
            items_text += "\n".join(f"- {i.title}" for i in news_items[:30])

        prompt = f"""You are a financial analyst. Write a daily market brief in Korean based on the data below.
Format as markdown with these sections:
- 주요 요약 (3-5 bullet points)
- 공시 분석 (if DART data exists)
- 뉴스 분석 (if news data exists)
- 종합 의견

Keep it concise (under 500 words).

{items_text}"""

        response = self.client.models.generate_content(model=self.model_name, contents=prompt)
        return response.text


def _parse_analysis(text: str, stock_code: str = "") -> AnalysisResult:
    """Parse structured response into AnalysisResult."""
    summary = ""
    sentiment = "neutral"
    key_points = []

    section = ""
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("SUMMARY:"):
            section = "summary"
            rest = stripped[len("SUMMARY:"):].strip()
            if rest:
                summary = rest
            continue
        elif stripped.startswith("SENTIMENT:"):
            section = "sentiment"
            rest = stripped[len("SENTIMENT:"):].strip().lower()
            if rest in ("positive", "negative", "neutral"):
                sentiment = rest
            continue
        elif stripped.startswith("KEY_POINTS:"):
            section = "points"
            continue

        if section == "summary" and stripped:
            summary += (" " + stripped) if summary else stripped
        elif section == "sentiment" and stripped:
            val = stripped.lower()
            if val in ("positive", "negative", "neutral"):
                sentiment = val
        elif section == "points" and stripped.startswith("- "):
            key_points.append(stripped[2:])

    return AnalysisResult(
        summary=summary or text[:200],
        sentiment=sentiment,
        key_points=key_points,
        stock_code=stock_code,
    )
