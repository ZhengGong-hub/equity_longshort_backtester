import pandas as pd

from momentum_backtester.adapters.sp500_github_adapter import load_tiny_sample, load_sp500_data_wrds
from momentum_backtester.backtester import Backtester
from momentum_backtester.signals import close_to_close_momentum
from momentum_backtester.ranking import cross_sectional_rank
from momentum_backtester.aggregation import long_short_top_bottom
from momentum_backtester.costs import turnover_costs

def main() -> None:
    data = load_sp500_data_wrds()
    sp500_universes = data["sp500_universes"]
    retoto_df_wide = data["retoto_df_wide"]
    retctc_df_wide = data["retctc_df_wide"]
    adjclose_df_wide = data["adjclose_df_wide"]
    adjopen_df_wide = data["adjopen_df_wide"]
    sector_df_wide = data["sector_df_wide"]

    bt = Backtester(
        retoto_df_wide=retoto_df_wide,
        retctc_df_wide=retctc_df_wide,
        adjclose_df_wide=adjclose_df_wide,
        adjopen_df_wide=adjopen_df_wide,
        sector_df_wide=sector_df_wide,
        signal=lambda px: close_to_close_momentum(
            px, 
            lookback_days=2, 
            skip=1),
        ranker=cross_sectional_rank,
        aggregator=lambda ranks, sectors: long_short_top_bottom(
            ranks, 
            sectors, 
            top_n=50, 
            bottom_n=50),
        costs=lambda w: turnover_costs(w, 0.0),
        rebal_freq="M",
    )
    results = bt.run()
    print(results)
    summary = {
        "start": results["net_returns"].index.min(),
        "end": results["net_returns"].index.max(),
        "n_days": int(results["net_returns"].shape[0]),
        "cum_return": float((1 + results["net_returns"]).prod() - 1.0),
    }
    print(summary)
    
if __name__ == "__main__":
    main()