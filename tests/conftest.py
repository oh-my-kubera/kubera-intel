"""Shared test fixtures."""

import pytest


@pytest.fixture()
def intel_dir(tmp_path, monkeypatch):
    """Set up a temporary .intel directory."""
    monkeypatch.chdir(tmp_path)
    d = tmp_path / ".intel"
    d.mkdir()
    (d / "reports").mkdir()
    (d / "data").mkdir()
    return d
