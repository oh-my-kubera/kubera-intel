# core — Business logic modules

## Modules

| Module | Purpose |
|--------|---------|
| config.py | Settings via pydantic-settings (INTEL_ env prefix) + directory helpers |
| credentials.py | JSON-based credential CRUD (same pattern as kubera-core) |
| watchlist.py | Stock watchlist CRUD — code + name pairs |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| collectors/ | Data source adapters (DART, Naver News). Each returns `list[CollectedItem]` |
| analyzer/ | Gemini AI — summarization, sentiment analysis |
| reporter/ | Markdown report generation using analyzer output |

## Data Flow

collectors → `CollectedItem` list → analyzer → `AnalysisResult` → reporter → markdown file

All persistent data goes under `.intel/` (data/, reports/, credentials.json, watchlist.json).
