"""Tests for data retention cleanup."""

from __future__ import annotations

import os
import time

from intel.core.cleanup import cleanup_old_files


class TestCleanup:
    def test_deletes_old_files(self, intel_dir):
        # Create files in data and reports
        old_data = intel_dir / "data" / "dart-2026-01-01.json"
        old_report = intel_dir / "reports" / "daily-2026-01-01.md"
        old_data.write_text("{}")
        old_report.write_text("# Report")

        # Set mtime to 60 days ago
        old_time = time.time() - (60 * 86400)
        os.utime(old_data, (old_time, old_time))
        os.utime(old_report, (old_time, old_time))

        deleted = cleanup_old_files(retention_days=30)
        assert deleted == 2
        assert not old_data.exists()
        assert not old_report.exists()

    def test_keeps_recent_files(self, intel_dir):
        recent = intel_dir / "data" / "dart-2026-02-28.json"
        recent.write_text("{}")

        deleted = cleanup_old_files(retention_days=30)
        assert deleted == 0
        assert recent.exists()

    def test_mixed_old_and_new(self, intel_dir):
        old_file = intel_dir / "data" / "old.json"
        new_file = intel_dir / "data" / "new.json"
        old_file.write_text("{}")
        new_file.write_text("{}")

        old_time = time.time() - (60 * 86400)
        os.utime(old_file, (old_time, old_time))

        deleted = cleanup_old_files(retention_days=30)
        assert deleted == 1
        assert not old_file.exists()
        assert new_file.exists()

    def test_empty_directories(self, intel_dir):
        deleted = cleanup_old_files(retention_days=30)
        assert deleted == 0
