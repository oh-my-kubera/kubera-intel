# intel — Financial data collection and AI-powered analysis CLI

Cron-driven CLI tool. Collects DART disclosures + Naver news, analyzes with Gemini,
generates markdown reports. No daemon, no database — JSON cache + markdown output.

## Flow

```
cron → kubera-intel collect {dart,news} → .intel/data/{source}-{date}.json
     → kubera-intel report {daily,stock} → .intel/reports/{type}-{date}.md
```

## Package Layout

| Directory | Purpose |
|-----------|---------|
| cli/ | argparse entry point + all subcommands |
| core/ | Business logic: config, credentials, watchlist, collectors, analyzer, reporter |

## Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| No DB | JSON files | MVP simplicity, e2-micro memory constraints |
| google-genai SDK | v1.x Client API | google-generativeai is deprecated |
| Markdown reports | .intel/reports/ | Human-readable, git-friendly |
| Korean output | Gemini prompt | Target users are Korean investors |
