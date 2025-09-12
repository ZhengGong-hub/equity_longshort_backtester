from __future__ import annotations

import pandas as pd

from momentum_backtester.adapters.sp500_github_adapter import load_tiny_sample
from momentum_backtester.backtester import Backtester, BacktestConfig
from momentum_backtester.signals import close_to_close_momentum
from momentum_backtester.ranking import cross_sectional_rank
from momentum_backtester.aggregation import long_short_top_bottom
from momentum_backtester.costs import turnover_costs


def main() -> None:
    data = load_tiny_sample()
    bt = Backtester(
        prices=data.prices,
        sectors=data.sectors,
        universe=data.universe,
        signal=lambda px: close_to_close_momentum(px, 12, 1),
        ranker=cross_sectional_rank,
        aggregator=lambda ranks, sectors: long_short_top_bottom(ranks, sectors, 2, 2),
        costs=lambda w: turnover_costs(w, 10.0),
        config=BacktestConfig(top_n=2, bottom_n=2),
    )
    results = bt.run()
    summary = {
        "start": results["net_returns"].index.min(),
        "end": results["net_returns"].index.max(),
        "n_days": int(results["net_returns"].shape[0]),
        "cum_return": float((1 + results["net_returns"]).prod() - 1.0),
    }
    print(summary)


if __name__ == "__main__":
    main()


