"""Tests for credential storage."""

from intel.core.credentials import get_credential, load_credentials, remove_credential, save_credential


class TestLoadCredentials:
    def test_empty_when_no_file(self, intel_dir):
        assert load_credentials() == []

    def test_loads_valid_json(self, intel_dir):
        path = intel_dir / "credentials.json"
        path.write_text('[{"provider": "dart", "api_key": "test"}]')
        result = load_credentials()
        assert len(result) == 1
        assert result[0]["provider"] == "dart"

    def test_returns_empty_on_invalid_json(self, intel_dir):
        path = intel_dir / "credentials.json"
        path.write_text("not json")
        assert load_credentials() == []


class TestSaveCredential:
    def test_creates_file(self, intel_dir):
        save_credential({"provider": "dart", "api_key": "abc"})
        result = load_credentials()
        assert len(result) == 1
        assert result[0]["api_key"] == "abc"

    def test_replaces_existing(self, intel_dir):
        save_credential({"provider": "dart", "api_key": "old"})
        save_credential({"provider": "dart", "api_key": "new"})
        result = load_credentials()
        assert len(result) == 1
        assert result[0]["api_key"] == "new"


class TestGetCredential:
    def test_returns_none_when_missing(self, intel_dir):
        assert get_credential("dart") is None

    def test_returns_matching_provider(self, intel_dir):
        save_credential({"provider": "dart", "api_key": "abc"})
        result = get_credential("dart")
        assert result is not None
        assert result["api_key"] == "abc"


class TestRemoveCredential:
    def test_removes_existing(self, intel_dir):
        save_credential({"provider": "dart", "api_key": "abc"})
        assert remove_credential("dart") is True
        assert get_credential("dart") is None

    def test_returns_false_when_missing(self, intel_dir):
        assert remove_credential("dart") is False
