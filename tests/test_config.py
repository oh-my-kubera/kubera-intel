"""Tests for config module."""

from intel.core.config import Settings, intel_dir


class TestSettings:
    def test_defaults(self):
        settings = Settings(_env_file=None)
        assert settings.dart_max_results == 20
        assert settings.naver_max_results == 20
        assert settings.gemini_model == "gemini-2.0-flash"
        assert settings.report_lang == "ko"
        assert settings.debug is False

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("INTEL_DART_MAX_RESULTS", "50")
        monkeypatch.setenv("INTEL_DEBUG", "true")
        settings = Settings(_env_file=None)
        assert settings.dart_max_results == 50
        assert settings.debug is True


class TestIntelDir:
    def test_creates_directory(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        d = intel_dir()
        assert d.exists()
        assert d.name == ".intel"
