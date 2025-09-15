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

# Reflections:
- I implemented the strategy in the classic setting as specified in the sheet. I did not have the time to fine tune any parameters, but the function class is written in such a way that it should be grid-searchable.
- several ways can be tried to make the strat work better: adjust the momentum by beta/vol, coupled with fundamentals/volumes to intentionally avoid meme names, get help with MA line/vol evolution, double-sort with size might help as well.
- I used WRDS freely available data to build the backtester. identifier: gvkey, permno.
- The strategy does not work well at its current setting, reasons could be multi-faceted: 
- infra high level: dockerize, deploy on AWS/Azure, crontab or airflow to run it daily. Useful intermediate results should be saved in a db or simply local fs.
- on coding level: have mypy, linter, CI flow, pytest to ensure compilability and coding standard. Separate test env and prod env. 
- if possible: do not fetch data directly from the source popping into the backtester, instead we should first save the data locally and let the backetester fetch from locally. In this way, we maintain raw_input_db, backtester, output_db. In parallel, we can per-calculate useful factors and pop into db so that backtester focuses only on backtesting and report gen.  


# TODO:
- make it more general
- incorporate fundamentals data 
- need to do robust testing with dummy file, to make sure that the shift() is done all correctly.
- overlay with macro: i.e. risk-free rate
- plot should follow a certain style
- ruff, mypy, makefile

