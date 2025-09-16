# momentum-backtester

Sector‑neutral momentum backtests the right way: typed, testable, reproducible. Clean architecture makes it easy to extend signals, ranking, and portfolio construction.

---

## Overview

This repository provides a modular, S&P 500‑focused momentum backtesting framework. You can plug in your own:
- Signal function (e.g., price momentum)
- Cross‑sectional ranker
- Portfolio aggregator (long‑only or long/short, sector‑neutral options)
- Transaction cost model 
(should be fully OoP)

It supports daily or monthly rebalancing, sector attribution, and produces analysis charts and summary statistics.

## Installation

Prerequisites:
- Python 3.10+
- Access to WRDS (with a valid token in environment)

Install dependencies (pip or uv):

```bash
# using pip
pip install -e .[dev]

# or using uv (if you prefer)
uv pip install -e .[dev]
```

## Quickstart

1. Export your WRDS credentials (or place them in a `.env` that your shell loads):

```bash
export WRDS_USERNAME=your_user
export WRDS_PASSWORD=your_password
```

2. Run a backtest and generate reports:

```bash
python scripts/run_backtester.py
```

Outputs (plots and metrics) are written to `output/`.

## How it works

At a high level:
- Rebalance dates are generated from a fixed calendar (daily or month‑end)
- Signals are computed from point‑in‑time prices (12‑1 momentum by default)
- Signals are ranked cross‑sectionally per date
- Weights are built via an aggregator (long‑only or sector‑neutral long/short)
- Portfolio returns are computed, costs are applied based on turnover
- Analysis module saves charts (NAV, SPY overlay, rolling beta, turnover) and prints summary stats

Key script:
- `scripts/run_backtester.py` — end‑to‑end example using WRDS S&P 500 data

Demo script:
- `notebooks/demo.ipynb` — end‑to‑end example using WRDS S&P 500 data

Core modules:
- `src/momentum_backtester/backtester.py` — orchestrates the backtest loop
- `src/momentum_backtester/signals.py` — e.g., `price_momentum(lookback_months=11, skip=1)`
- `src/momentum_backtester/ranking.py` — cross‑sectional ranking helpers
- `src/momentum_backtester/aggregation.py` — portfolio construction (long‑only and sector‑neutral long/short)
- `src/momentum_backtester/costs.py` — turnover‑based transaction costs
- `src/momentum_backtester/analysis.py` — metrics and plots
- `src/momentum_backtester/adapters/` — data loading utilities (S&P 500 universe, sectors)

## Configuration knobs

You can customize the strategy by editing `scripts/run_backtester.py`:
- Rebalance frequency: `rebal_freq="D"` or `"M"`
- Signal: `price_momentum(prices, lookback_months=11, skip=1)`
- Ranker: `cross_sectional_rank`
- Aggregators:
  - `long_only(top_pctg=20)`
  - `long_short_top_bottom_sector_neutral(top_pctg=20, bottom_pctg=20)`
- Transaction costs: `turnover_costs(weights, bps_per_turnover)`

## Outputs and metrics

Generated to `output/` by `Analysis`:
- NAV chart (gross vs net, with optional SPY overlay)
- SPY price chart
- Rolling beta of strategy vs SPY
- Total turnover
- Summary metrics: CAGR, annualized vol, Sharpe (with configurable risk‑free), max drawdown, alpha/beta

## Notes on data

The adapter pulls a point‑in‑time S&P 500 universe annual frequency, sector labels, and price series via WRDS. Identifiers used include `gvkey` and `permno`. You can swap in your own data adapter as long as you can provide wide DataFrames for prices/returns and sector labels.


# Reflections:
- wide format, despite advantages of vectorization, seems to have a difficult time dealing with delisting.
- I implemented the strategy in the classic setting as specified in the sheet. I did not have the time to fine tune any parameters, but the function class is written in such a way that it should be grid-searchable.
- I used WRDS freely available data to build the backtester. identifier: gvkey, permno. In this project, I used a github package that wraps the WRDS API to fetch the data.
## Strategy Rationale and Limitations

The current strategy implements a classic cross-sectional momentum approach, ranking stocks by their past 12-1 month returns and constructing portfolios based on these ranks. This specification is chosen for its simplicity and its strong historical performance. However, in practice, the strategy does not perform robustly under the current settings. Several factors may contribute to this:

- **Parameter Sensitivity:** The lookback and skip parameters, as well as portfolio construction rules (e.g., top 20% long-only, or 20% long short sector neutral), are not optimized.
- **High Beta Exposure:** Simple momentum signals often load heavily on high-beta stocks.
- **Sector Concentration:** Momentum effects are frequently strongest at the sector level (e.g., tech vs. energy), ie. sector rotation. Without explicit sector controls, the strategy may become unintentionally concentrated, reducing diversification and increasing risk.
- **Delisting and Survivorship Bias:** Handling of delisted stocks and universe changes is challenging in wide-format data, potentially distorting results if not managed carefully.

## How the Strategy Could Be Improved

1. **Risk-Adjusted Momentum**
   - Adjust signals for each stock by their historical beta or volatility, reducing unintended risk exposures and isolating true momentum effects.

2. **Incorporate Fundamentals and Events**
   - Overlay fundamental metrics (e.g., earnings quality, size, liquidity) and earnings events. Might be able diversion from a pure technical driven strategy.

3. **Consider other factors like MAs**
   - Use moving averages or other technical overlays to time momentum exposure.

4. **Double-Sorting Approaches**
   - Combine momentum with other factors (e.g., size, value, margin) or sort within buckets to diversify risk and improve robustness.

- Infrastructure: The whole pipeline should be dockerized and deployed on AWS or Azure. A scheduler like crontab or Airflow can trigger the workflow daily after market close. Intermediate results (raw data, clean data, signals, reports) should be saved to a database or local filesystem so they are reproducible and auditable.
- Coding practices: Enforce quality with mypy, a linter, pytest, and CI. Maintain separate environments for testing and production to avoid accidental breakage.
- Data workflow: The backtester should not fetch data directly from the vendor. Instead, first store raw inputs in a dedicated “raw_input_db.” The ETL process then cleans and enriches the data which are stored in a “feature/factors_table.” The backtester consumes only these prepared datasets and writes outputs (signals, attribution, performance) into an “output_db.” This separation keeps ETL and strategy logic cleanly decoupled.


# TODO:
- make it more general and OoP
- overlay with fundamentals data 
- need to do robust testing with dummy file, to make sure that the shift() is done all correctly.
- overlay with macro: i.e. risk-free rate
- plot should follow a certain style
- ruff, mypy, makefile
- propoer logger
