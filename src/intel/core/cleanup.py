"""Data retention cleanup."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from pathlib import Path

from intel.core.config import data_dir, reports_dir

logger = logging.getLogger(__name__)


def cleanup_old_files(retention_days: int = 30) -> int:
    """Delete data and report files older than retention_days. Returns count deleted."""
    cutoff = datetime.now() - timedelta(days=retention_days)
    deleted = 0

    for directory in [data_dir(), reports_dir()]:
        if not directory.exists():
            continue
        for f in directory.iterdir():
            if not f.is_file():
                continue
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime < cutoff:
                f.unlink()
                logger.info("Deleted %s (modified %s)", f.name, mtime.date())
                deleted += 1

    return deleted
