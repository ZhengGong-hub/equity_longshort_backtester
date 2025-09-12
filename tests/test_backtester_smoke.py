from __future__ import annotations

from momentum_backtester.adapters.sp500_github_adapter import load_tiny_sample
from momentum_backtester.backtester import Backtester, BacktestConfig
from momentum_backtester.signals import close_to_close_momentum
from momentum_backtester.ranking import cross_sectional_rank
from momentum_backtester.aggregation import long_short_top_bottom
from momentum_backtester.costs import turnover_costs


def test_smoke_backtest_runs():
    data = load_tiny_sample()
    bt = Backtester(
        prices=data.prices,
        sectors=data.sectors,
        universe=data.universe,
        signal=lambda px: close_to_close_momentum(px, 3, 1),
        ranker=cross_sectional_rank,
        aggregator=lambda ranks, sectors: long_short_top_bottom(ranks, sectors, 1, 1),
        costs=lambda w: turnover_costs(w, 5.0),
        config=BacktestConfig(top_n=1, bottom_n=1),
    )
    results = bt.run()
    assert "net_returns" in results
    assert results["net_returns"].shape[0] > 0


