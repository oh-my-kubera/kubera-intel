"""Tests for watchlist management."""

from intel.core.watchlist import add_to_watchlist, load_watchlist, remove_from_watchlist


class TestWatchlist:
    def test_empty_by_default(self, intel_dir):
        assert load_watchlist() == []

    def test_add_item(self, intel_dir):
        add_to_watchlist("005930", "삼성전자")
        items = load_watchlist()
        assert len(items) == 1
        assert items[0]["code"] == "005930"
        assert items[0]["name"] == "삼성전자"

    def test_add_replaces_by_code(self, intel_dir):
        add_to_watchlist("005930", "삼성전자")
        add_to_watchlist("005930", "Samsung")
        items = load_watchlist()
        assert len(items) == 1
        assert items[0]["name"] == "Samsung"

    def test_add_multiple(self, intel_dir):
        add_to_watchlist("005930", "삼성전자")
        add_to_watchlist("000660", "SK하이닉스")
        assert len(load_watchlist()) == 2

    def test_remove_existing(self, intel_dir):
        add_to_watchlist("005930", "삼성전자")
        assert remove_from_watchlist("005930") is True
        assert load_watchlist() == []

    def test_remove_nonexistent(self, intel_dir):
        assert remove_from_watchlist("999999") is False
