import pandas as pd

from momentum_backtester.adapters.sp500_github_adapter import load_tiny_sample, load_sp500_data_wrds
from momentum_backtester.backtester import Backtester
from momentum_backtester.signals import price_momentum
from momentum_backtester.ranking import cross_sectional_rank
from momentum_backtester.aggregation import long_short_top_bottom_sector_neutral, long_only
from momentum_backtester.costs import turnover_costs
from momentum_backtester.analysis import Analysis

def main() -> None:
    data = load_sp500_data_wrds(start_year=2009, end_year=2024)
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
        signal=lambda px: price_momentum(
            px, 
            lookback_months=11, 
            skip=1),
        ranker=cross_sectional_rank,
        # aggregator=lambda ranks, sectors: long_short_top_bottom_sector_neutral(
        #     ranks, 
        #     sectors, 
        #     top_pctg=20, 
        #     bottom_pctg=20),
        aggregator=lambda ranks, sectors: long_only(
            ranks, 
            sectors, 
            top_pctg=20),
        costs=lambda w: turnover_costs(w, 10.0),
        rebal_freq="D",
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

    # start analysis
    analysis = Analysis(output_dir="output")
    analysis.cagr(results["net_returns"], 252)
    analysis.annual_vol(results["net_returns"], 252)
    analysis.sharpe(results["net_returns"], 0.04, 252)
    analysis.max_drawdown(results["net_returns"])
    analysis.nav_chart(results["gross_returns"], results["net_returns"], incl_spy=True, spy_daily=data["spy_daily"])
    analysis.spy_chart(data["spy_daily"])
    analysis.against_spy(results["net_returns"], data["spy_daily"])
    analysis.rolling_beta(results["net_returns"], data["spy_daily"])
    analysis.return_attr_sector(results["weights"], data["sector_df_wide"], results["retoto_df_wide"], results["gross_returns"])
    analysis.total_turnover(results["weights"])

if __name__ == "__main__":
    main()