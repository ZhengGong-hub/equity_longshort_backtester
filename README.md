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

# Run a backtest (tiny data)
python scripts/run_backtest.py
```

## structure of backtester

- 1: get rebalancing date
- 2: get signal -> save signal file
    in the signal file, the date represents at the starting of date, the signal file is already accessible.

# TODO:
- make it more general
- incorporate fundamentals data 
- need to do robust testing with dummy file, to make sure that the shift() is done all correctly.