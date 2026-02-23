"""DART OpenAPI collector."""

from __future__ import annotations

from datetime import date, timedelta

import httpx

from intel.core.collectors import CollectedItem


class DartCollector:
    BASE_URL = "https://opendart.fss.or.kr/api"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def collect(
        self,
        stock_code: str = "",
        days_back: int = 1,
        max_results: int = 20,
    ) -> list[CollectedItem]:
        """Collect recent DART disclosures."""
        end = date.today()
        begin = end - timedelta(days=days_back)

        params: dict[str, str | int] = {
            "crtfc_key": self.api_key,
            "bgn_de": begin.strftime("%Y%m%d"),
            "end_de": end.strftime("%Y%m%d"),
            "page_count": max_results,
            "type": "json",
        }
        if stock_code:
            params["stock_code"] = stock_code

        response = httpx.get(
            f"{self.BASE_URL}/list.json",
            params=params,
            timeout=10.0,
        )
        if response.status_code != 200:
            return []

        data = response.json()
        status = data.get("status")
        if status != "000":
            # "013" = no data, others = error
            return []

        items = []
        for entry in data.get("list", []):
            rcept_no = entry.get("rcept_no", "")
            items.append(
                CollectedItem(
                    source="dart",
                    title=entry.get("report_nm", ""),
                    url=f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept_no}",
                    published=_format_date(entry.get("rcept_dt", "")),
                    content=entry.get("report_nm", ""),
                    stock_code=entry.get("stock_code", ""),
                    metadata={
                        "corp_name": entry.get("corp_name", ""),
                        "corp_code": entry.get("corp_code", ""),
                        "rcept_no": rcept_no,
                        "flr_nm": entry.get("flr_nm", ""),
                    },
                )
            )
        return items


def _format_date(raw: str) -> str:
    """Convert '20260223' to '2026-02-23'."""
    if len(raw) == 8:
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
    return raw
