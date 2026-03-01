# kubera-intel

Financial data collection and AI-powered analysis tool.

Collects DART disclosures, Naver news, and generates AI-summarized reports using Gemini.

## Install

```bash
uv tool install kubera-intel
```

## Setup

```bash
kubera-intel credential add dart
kubera-intel credential add naver
kubera-intel credential add gemini
kubera-intel watchlist add 005930 삼성전자
```

## Usage

```bash
# Collect data
kubera-intel collect dart
kubera-intel collect news

# Generate reports
kubera-intel report daily
kubera-intel report stock 005930
```

## Cron Setup (GCP)

See `crontab.example` for the full schedule. Install with:

```bash
crontab crontab.example
```

Schedule (KST, weekdays only):

| Time | Job |
|------|-----|
| 08:30 | Collect DART disclosures |
| 08:35 | Collect Naver news |
| 09:00 | Generate daily morning report |
| 14:00 | Refresh news |
| 15:45 | Collect DART + news (final) |
| 16:00 | Generate market close report |

## License

MIT
