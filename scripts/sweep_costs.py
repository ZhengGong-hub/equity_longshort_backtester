from __future__ import annotations

from typing import List

from momentum_backtester.adapters.sp500_github_adapter import load_tiny_sample
from momentum_backtester.backtester import Backtester, BacktestConfig
from momentum_backtester.signals import close_to_close_momentum
from momentum_backtester.ranking import cross_sectional_rank
from momentum_backtester.aggregation import long_short_top_bottom
from momentum_backtester.costs import turnover_costs


def run_for_cost(cost_bps: float) -> float:
    data = load_tiny_sample()
    bt = Backtester(
        prices=data.prices,
        sectors=data.sectors,
        universe=data.universe,
        signal=lambda px: close_to_close_momentum(px, 12, 1),
        ranker=cross_sectional_rank,
        aggregator=lambda ranks, sectors: long_short_top_bottom(ranks, sectors, 2, 2),
        costs=lambda w: turnover_costs(w, cost_bps),
        config=BacktestConfig(top_n=2, bottom_n=2),
    )
    results = bt.run()
    return float((1 + results["net_returns"]).prod() - 1.0)


def main() -> None:
    grid: List[float] = [0, 5, 10, 25, 50]
    for bps in grid:
        cum = run_for_cost(bps)
        print({"bps": bps, "cum_return": cum})


if __name__ == "__main__":
    main()


