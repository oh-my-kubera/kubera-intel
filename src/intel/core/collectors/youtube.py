"""YouTube Data API v3 collector (Phase 2)."""

from __future__ import annotations

from intel.core.collectors import CollectedItem


class YouTubeCollector:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def collect(self, **kwargs) -> list[CollectedItem]:
        raise NotImplementedError("YouTube collector is planned for Phase 2")
