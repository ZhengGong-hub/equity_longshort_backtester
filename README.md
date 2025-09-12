# momentum-backtester

Sector‑neutral momentum backtests built the right way: typed, tested, reproducible, and CI‑enforced. Clean architecture makes it easy to extend signals, ranking, and portfolio construction.

## Features
- Point‑in‑time S&P 500 universe + GICS sectors.
- Pluggable components: Signal → Rank → Aggregate → Costs.
- Monthly rebalancing, turnover‑based costs, sector attribution.
- Metrics: CAGR, vol, Sharpe, max DD, alpha/beta, rolling beta.
- Reproducible runs (fixed calendar, pinned deps, Docker image).

## Quickstart
```bash
# 1) Install tooling
uv venv && uv pip install -e .[dev]
pre-commit install

# 2) Run tests
pytest -q

# 3) Run a backtest (tiny data)
python scripts/run_backtest.py
```

## Repo layout
See the file tree in the issue or the project description. Core code lives under `src/momentum_backtester`.

## Notes
- Use `.env.example` as a template for runtime settings.
- Dockerfile builds a self‑contained test image.
- CI runs lint, type‑check, and tests on pushes and PRs.
