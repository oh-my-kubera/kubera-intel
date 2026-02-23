# collectors — External data source adapters

Each collector implements `collect(**kwargs) -> list[CollectedItem]`.
CollectedItem is the shared dataclass defined in `__init__.py`.

## Collectors

| Collector | Source | API | Auth |
|-----------|--------|-----|------|
| DartCollector | DART 공시 | `/api/list.json` | `crtfc_key` query param |
| NaverNewsCollector | Naver News | `/v1/search/news.json` | `X-Naver-Client-Id/Secret` headers |
| youtube.py | YouTube (stub) | — | Phase 2 |

## Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| httpx over requests | sync httpx.get | Already a dependency, lighter than requests |
| HTML stripping in news | regex + html.unescape | No extra dependency needed |
| Date parsing | email.utils for RFC 2822 | stdlib, handles Naver pubDate format |
