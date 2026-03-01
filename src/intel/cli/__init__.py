"""kubera-intel CLI entry point."""

from __future__ import annotations

import argparse

from importlib.metadata import version as get_version


def main() -> None:
    parser = argparse.ArgumentParser(prog="kubera-intel", description="Financial data collection and AI analysis")
    parser.add_argument("-V", "--version", action="version", version=f"kubera-intel {get_version('kubera-intel')}")
    subparsers = parser.add_subparsers(dest="command")

    # kubera-intel credential
    cred_parser = subparsers.add_parser("credential", help="Manage API credentials")
    cred_sub = cred_parser.add_subparsers(dest="cred_command")

    cred_add = cred_sub.add_parser("add", help="Add a credential")
    cred_add.add_argument("provider", type=str, help="Provider name (dart, naver, youtube, gemini)")

    cred_sub.add_parser("list", help="List credentials")

    cred_remove = cred_sub.add_parser("remove", help="Remove a credential")
    cred_remove.add_argument("provider", type=str, help="Provider name")

    # kubera-intel watchlist
    watch_parser = subparsers.add_parser("watchlist", help="Manage stock watchlist")
    watch_sub = watch_parser.add_subparsers(dest="watch_command")

    watch_add = watch_sub.add_parser("add", help="Add a stock")
    watch_add.add_argument("code", type=str, help="Stock code (e.g. 005930)")
    watch_add.add_argument("name", type=str, nargs="?", default="", help="Stock name (e.g. 삼성전자)")

    watch_sub.add_parser("list", help="List watchlist")

    watch_remove = watch_sub.add_parser("remove", help="Remove a stock")
    watch_remove.add_argument("code", type=str, help="Stock code")

    # kubera-intel collect
    collect_parser = subparsers.add_parser("collect", help="Collect data from sources")
    collect_sub = collect_parser.add_subparsers(dest="collect_command")

    collect_dart = collect_sub.add_parser("dart", help="Collect DART disclosures")
    collect_dart.add_argument("--stock", type=str, default=None, help="Specific stock code")

    collect_news = collect_sub.add_parser("news", help="Collect Naver news")
    collect_news.add_argument("--query", type=str, default=None, help="Custom search query")

    collect_yt = collect_sub.add_parser("youtube", help="Collect YouTube videos")
    collect_yt.add_argument("--query", type=str, default=None, help="Custom search query")

    # kubera-intel report
    report_parser = subparsers.add_parser("report", help="Generate reports")
    report_sub = report_parser.add_subparsers(dest="report_command")

    report_daily = report_sub.add_parser("daily", help="Generate daily market report")
    report_daily.add_argument("--market-close", action="store_true", help="Market close edition")

    report_stock = report_sub.add_parser("stock", help="Generate stock deep dive report")
    report_stock.add_argument("code", type=str, help="Stock code (e.g. 005930)")

    # kubera-intel cleanup
    cleanup_parser = subparsers.add_parser("cleanup", help="Delete old data and reports")
    cleanup_parser.add_argument("--days", type=int, default=None, help="Retention days (default: INTEL_RETENTION_DAYS or 30)")

    args = parser.parse_args()

    # Setup logging early (before any command runs)
    from intel.core.config import get_settings, setup_logging
    settings = get_settings()
    setup_logging(debug=settings.debug)

    if args.command == "credential":
        from intel.cli.commands import cmd_credential
        cmd_credential(args)
    elif args.command == "watchlist":
        from intel.cli.commands import cmd_watchlist
        cmd_watchlist(args)
    elif args.command == "collect":
        from intel.cli.commands import cmd_collect
        cmd_collect(args)
    elif args.command == "report":
        from intel.cli.commands import cmd_report
        cmd_report(args)
    elif args.command == "cleanup":
        from intel.core.cleanup import cleanup_old_files
        days = args.days if args.days is not None else settings.retention_days
        deleted = cleanup_old_files(retention_days=days)
        print(f"Cleanup complete: {deleted} file(s) deleted (retention: {days} days)")
    else:
        parser.print_help()
