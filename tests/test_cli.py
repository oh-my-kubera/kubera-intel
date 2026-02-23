"""Tests for CLI entry point."""

import sys

from intel.cli import main


class TestCLI:
    def test_help(self, capsys):
        sys.argv = ["kubera-intel", "--help"]
        try:
            main()
        except SystemExit:
            pass
        captured = capsys.readouterr()
        assert "credential" in captured.out
        assert "watchlist" in captured.out
        assert "collect" in captured.out
        assert "report" in captured.out

    def test_version(self, capsys):
        sys.argv = ["kubera-intel", "--version"]
        try:
            main()
        except SystemExit:
            pass
        captured = capsys.readouterr()
        assert "kubera-intel" in captured.out

    def test_no_command_shows_help(self, capsys):
        sys.argv = ["kubera-intel"]
        main()
        captured = capsys.readouterr()
        assert "usage" in captured.out.lower() or "kubera-intel" in captured.out
