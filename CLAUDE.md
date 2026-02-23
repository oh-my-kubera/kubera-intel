# kubera-intel

Financial data collection and AI-powered analysis tool for the kubera ecosystem.

## Build & Test
- Package manager: uv
- Run tests: `uv run pytest`
- Run single test: `uv run pytest tests/test_xxx.py`
- Dev run: `uv run kubera-intel --help`

## Deployment Constraints
- Runs on GCP e2-micro VM alongside kubera-core (1GB RAM shared)
- CLI tool executed via cron — not a daemon
- Must exit cleanly after each run
- Runtime data in `.intel/` directory

## Security
- Credential keys: CLI only for input. Never log API keys.
