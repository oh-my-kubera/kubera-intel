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

## Cron Example

```bash
# Daily at 7am KST
0 7 * * * cd /home/user/kubera-intel && kubera-intel collect dart && kubera-intel collect news && kubera-intel report daily
```

## License

MIT
