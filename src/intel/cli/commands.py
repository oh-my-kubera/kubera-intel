"""CLI subcommands."""

from __future__ import annotations

import argparse
import sys

PROVIDER_FIELDS: dict[str, list[dict]] = {
    "dart": [
        {"name": "api_key", "required": True, "prompt": "DART API Key", "secret": True},
    ],
    "naver": [
        {"name": "client_id", "required": True, "prompt": "Naver Client ID"},
        {"name": "client_secret", "required": True, "prompt": "Naver Client Secret", "secret": True},
    ],
    "youtube": [
        {"name": "api_key", "required": True, "prompt": "YouTube API Key", "secret": True},
    ],
    "gemini": [
        {"name": "api_key", "required": True, "prompt": "Gemini API Key", "secret": True},
    ],
}


def cmd_credential(args: argparse.Namespace) -> None:
    """Manage credentials."""
    if args.cred_command == "add":
        _cmd_credential_add(args)
    elif args.cred_command == "list":
        _cmd_credential_list()
    elif args.cred_command == "remove":
        _cmd_credential_remove(args)
    else:
        print("Usage: kubera-intel credential {add,list,remove}")


def _cmd_credential_add(args: argparse.Namespace) -> None:
    """Interactively add a credential for a provider."""
    import getpass

    provider = args.provider
    if provider not in PROVIDER_FIELDS:
        print(f"Error: unsupported provider '{provider}'. Supported: {', '.join(PROVIDER_FIELDS)}")
        sys.exit(1)

    fields = PROVIDER_FIELDS[provider]
    credential: dict[str, str] = {"provider": provider}

    for field in fields:
        prompt = field["prompt"] + ": "
        if field.get("secret"):
            value = getpass.getpass(prompt)
            if value:
                print(f"  -> {len(value)} chars")
        else:
            value = input(prompt)
        if field["required"] and not value:
            print(f"Error: '{field['name']}' is required.")
            sys.exit(1)
        if value:
            credential[field["name"]] = value

    from intel.core.credentials import save_credential
    save_credential(credential)
    print(f"\nCredential for '{provider}' saved.")


def _cmd_credential_list() -> None:
    """List saved credentials."""
    from intel.core.credentials import load_credentials

    credentials = load_credentials()
    if not credentials:
        print("No credentials stored.")
        return

    secret_fields = set()
    for fields in PROVIDER_FIELDS.values():
        for f in fields:
            if f.get("secret"):
                secret_fields.add(f["name"])

    print(f"{'Provider':<12} {'Key':<20} {'Value'}")
    print("-" * 50)
    for cred in credentials:
        provider = cred.get("provider", "")
        for key, value in cred.items():
            if key == "provider":
                continue
            display = "***" if key in secret_fields else value
            print(f"{provider:<12} {key:<20} {display}")
            provider = ""


def _cmd_credential_remove(args: argparse.Namespace) -> None:
    """Remove credentials for a provider."""
    from intel.core.credentials import remove_credential

    provider = args.provider
    if not remove_credential(provider):
        print(f"No credential found for provider '{provider}'.")
        sys.exit(1)
    print(f"Credential for '{provider}' removed.")


def cmd_watchlist(args: argparse.Namespace) -> None:
    """Manage stock watchlist."""
    if args.watch_command == "add":
        _cmd_watchlist_add(args)
    elif args.watch_command == "list":
        _cmd_watchlist_list()
    elif args.watch_command == "remove":
        _cmd_watchlist_remove(args)
    else:
        print("Usage: kubera-intel watchlist {add,list,remove}")


def _cmd_watchlist_add(args: argparse.Namespace) -> None:
    from intel.core.watchlist import add_to_watchlist
    add_to_watchlist(args.code, args.name)
    name_part = f" ({args.name})" if args.name else ""
    print(f"Added {args.code}{name_part} to watchlist.")


def _cmd_watchlist_list() -> None:
    from intel.core.watchlist import load_watchlist

    items = load_watchlist()
    if not items:
        print("Watchlist is empty.")
        return

    print(f"{'Code':<12} {'Name'}")
    print("-" * 30)
    for item in items:
        print(f"{item['code']:<12} {item.get('name', '')}")


def _cmd_watchlist_remove(args: argparse.Namespace) -> None:
    from intel.core.watchlist import remove_from_watchlist

    if not remove_from_watchlist(args.code):
        print(f"Stock '{args.code}' not in watchlist.")
        sys.exit(1)
    print(f"Removed {args.code} from watchlist.")


def cmd_collect(args: argparse.Namespace) -> None:
    """Collect data from sources."""
    if args.collect_command == "dart":
        _cmd_collect_dart(args)
    elif args.collect_command == "news":
        _cmd_collect_news(args)
    elif args.collect_command == "youtube":
        _cmd_collect_youtube(args)
    else:
        print("Usage: kubera-intel collect {dart,news,youtube}")


def _save_collected(items: list, source: str) -> None:
    """Save collected items to a dated JSON file."""
    import json
    from datetime import date

    from intel.core.config import data_dir

    today = date.today().isoformat()
    out_path = data_dir() / f"{source}-{today}.json"
    out_path.write_text(json.dumps([vars(item) for item in items], ensure_ascii=False, indent=2))
    print(f"Collected {len(items)} {source} items -> {out_path}")


def _require_credential(provider: str) -> dict:
    """Get credential or exit with helpful message."""
    from intel.core.credentials import get_credential

    credential = get_credential(provider)
    if not credential:
        print(f"Error: no {provider} credential. Run 'kubera-intel credential add {provider}' first.")
        sys.exit(1)
    return credential


def _get_watchlist_queries() -> list[str]:
    """Get search queries from watchlist or exit."""
    from intel.core.watchlist import load_watchlist

    watchlist = load_watchlist()
    if not watchlist:
        print("Error: watchlist is empty. Run 'kubera-intel watchlist add <CODE>' first.")
        sys.exit(1)
    return [item.get("name") or item["code"] for item in watchlist]


def _cmd_collect_dart(args: argparse.Namespace) -> None:
    """Collect DART disclosures."""
    from intel.core.collectors.dart import DartCollector
    from intel.core.watchlist import load_watchlist

    credential = _require_credential("dart")
    collector = DartCollector(api_key=credential["api_key"])

    if args.stock:
        codes = [args.stock]
    else:
        watchlist = load_watchlist()
        if not watchlist:
            print("Error: watchlist is empty. Run 'kubera-intel watchlist add <CODE>' first.")
            sys.exit(1)
        codes = [item["code"] for item in watchlist]

    all_items = []
    for code in codes:
        all_items.extend(collector.collect(stock_code=code))

    _save_collected(all_items, "dart")


def _cmd_collect_news(args: argparse.Namespace) -> None:
    """Collect Naver news."""
    from intel.core.collectors.news import NaverNewsCollector
    from intel.core.config import get_settings

    credential = _require_credential("naver")
    settings = get_settings()
    collector = NaverNewsCollector(
        client_id=credential["client_id"],
        client_secret=credential["client_secret"],
    )

    queries = [args.query] if args.query else _get_watchlist_queries()
    all_items = []
    for query in queries:
        all_items.extend(collector.collect(query=query, max_results=settings.naver_max_results))

    _save_collected(all_items, "news")


def _cmd_collect_youtube(args: argparse.Namespace) -> None:
    """Collect YouTube videos."""
    from intel.core.collectors.youtube import YouTubeCollector

    credential = _require_credential("youtube")
    collector = YouTubeCollector(api_key=credential["api_key"])

    queries = [args.query] if args.query else _get_watchlist_queries()
    all_items = []
    for query in queries:
        all_items.extend(collector.collect(query=query, max_results=10))

    _save_collected(all_items, "youtube")


def cmd_report(args: argparse.Namespace) -> None:
    """Generate reports."""
    if args.report_command == "daily":
        _cmd_report_daily(args)
    elif args.report_command == "stock":
        _cmd_report_stock(args)
    else:
        print("Usage: kubera-intel report {daily,stock}")


def _cmd_report_daily(args: argparse.Namespace) -> None:
    """Generate daily market report."""
    import json
    from datetime import date

    from intel.core.analyzer.gemini import GeminiAnalyzer
    from intel.core.collectors import CollectedItem
    from intel.core.config import data_dir, get_settings
    from intel.core.credentials import get_credential
    from intel.core.reporter.daily import DailyReporter

    gemini_cred = get_credential("gemini")
    if not gemini_cred:
        print("Error: no Gemini credential. Run 'kubera-intel credential add gemini' first.")
        sys.exit(1)

    settings = get_settings()
    today = date.today().isoformat()

    all_items = _load_today_data(today)
    if not all_items:
        print(f"No data found for {today}. Run 'kubera-intel collect' first.")
        sys.exit(1)

    analyzer = GeminiAnalyzer(api_key=gemini_cred["api_key"], model=settings.gemini_model)
    reporter = DailyReporter(analyzer=analyzer)
    path = reporter.generate(items=all_items, market_close=getattr(args, "market_close", False))
    print(f"Daily report saved: {path}")


def _cmd_report_stock(args: argparse.Namespace) -> None:
    """Generate stock deep dive report."""
    import json
    from datetime import date

    from intel.core.analyzer.gemini import GeminiAnalyzer
    from intel.core.collectors import CollectedItem
    from intel.core.config import get_settings
    from intel.core.credentials import get_credential
    from intel.core.reporter.stock import StockReporter
    from intel.core.watchlist import load_watchlist

    gemini_cred = get_credential("gemini")
    if not gemini_cred:
        print("Error: no Gemini credential. Run 'kubera-intel credential add gemini' first.")
        sys.exit(1)

    settings = get_settings()
    code = args.code
    today = date.today().isoformat()

    # Find stock name from watchlist
    watchlist = load_watchlist()
    stock_name = ""
    for item in watchlist:
        if item["code"] == code:
            stock_name = item.get("name", "")
            break

    all_items = _load_today_data(today)
    stock_items = [item for item in all_items if item.stock_code == code or code in item.title]
    if not stock_items:
        print(f"No data found for stock {code}. Run 'kubera-intel collect' first.")
        sys.exit(1)

    analyzer = GeminiAnalyzer(api_key=gemini_cred["api_key"], model=settings.gemini_model)
    reporter = StockReporter(analyzer=analyzer)
    path = reporter.generate(stock_code=code, stock_name=stock_name, items=stock_items)
    print(f"Stock report saved: {path}")


def _load_today_data(today: str) -> list:
    """Load all collected data files for a given date."""
    import json

    from intel.core.collectors import CollectedItem
    from intel.core.config import data_dir

    d = data_dir()
    all_items = []
    for path in d.glob(f"*-{today}.json"):
        try:
            raw = json.loads(path.read_text())
            for entry in raw:
                all_items.append(CollectedItem(**entry))
        except Exception:
            continue
    return all_items
