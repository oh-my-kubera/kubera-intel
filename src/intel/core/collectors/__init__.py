"""Data collectors."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CollectedItem:
    source: str
    title: str
    url: str
    published: str
    content: str = ""
    stock_code: str = ""
    metadata: dict = field(default_factory=dict)
