"""Watchlist management."""

from __future__ import annotations

import json
from pathlib import Path

from intel.core.config import intel_dir


def watchlist_path() -> Path:
    return intel_dir() / "watchlist.json"


def load_watchlist() -> list[dict]:
    path = watchlist_path()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        return data if isinstance(data, list) else []
    except Exception:
        return []


def add_to_watchlist(code: str, name: str = "") -> None:
    items = load_watchlist()
    items = [item for item in items if item.get("code") != code]
    items.append({"code": code, "name": name})
    _write_watchlist(items)


def remove_from_watchlist(code: str) -> bool:
    items = load_watchlist()
    remaining = [item for item in items if item.get("code") != code]
    if len(remaining) == len(items):
        return False
    _write_watchlist(remaining)
    return True


def _write_watchlist(items: list[dict]) -> None:
    watchlist_path().write_text(json.dumps(items, indent=2, ensure_ascii=False))
