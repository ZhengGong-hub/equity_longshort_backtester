from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Tuple

import numpy as np
import pandas as pd

from .utils import MonthEndCalendar


SignalFunc = Callable[[pd.DataFrame], pd.DataFrame]
RankFunc = Callable[[pd.DataFrame], pd.DataFrame]
AggFunc = Callable[[pd.DataFrame, pd.DataFrame], pd.DataFrame]
CostFunc = Callable[[pd.DataFrame, pd.DataFrame], pd.Series]

class Backtester:
    def __init__(
        self,
        retoto_df_wide: pd.DataFrame,
        retctc_df_wide: pd.DataFrame,
        adjclose_df_wide: pd.DataFrame,
        adjopen_df_wide: pd.DataFrame,
        sector_df_wide: pd.DataFrame,
        signal: SignalFunc,
        ranker: RankFunc,
        aggregator: AggFunc,
        costs: CostFunc,
        rebal_freq: str = "M",
    ) -> None:
        self.retoto_df_wide = retoto_df_wide.sort_index()
        self.retctc_df_wide = retctc_df_wide.sort_index()
        self.adjclose_df_wide = adjclose_df_wide.sort_index()
        self.adjopen_df_wide = adjopen_df_wide.sort_index()
        self.sector_df_wide = sector_df_wide.sort_index()
        self.signal = signal
        self.ranker = ranker
        self.aggregator = aggregator
        self.costs = costs
        self.calendar = MonthEndCalendar()
        self.rebal_freq = rebal_freq

    def run(self) -> Dict[str, pd.DataFrame | pd.Series]:
        if self.rebal_freq == "D":
            rebal_dates = self.calendar.day_ends(self.retctc_df_wide.index)
        elif self.rebal_freq == "M":
            rebal_dates = self.calendar.month_ends(self.retctc_df_wide.index)
        else:
            raise ValueError(f"Invalid rebalance frequency: {self.rebal_freq}")
        # print(rebal_dates)

        signals = self.signal(self.adjclose_df_wide)
        # print(signals.tail())

        ranks = self.ranker(signals.loc[rebal_dates])
        # print(ranks.tail())

        weights = self.aggregator(ranks, self.sector_df_wide)
        print(weights.tail())

        port_rets = (weights.reindex(self.retoto_df_wide.index).ffill().fillna(0.0) * self.retoto_df_wide.shift(-1)).sum(axis=1)

        tc = self.costs(weights)
        net_rets = port_rets - tc.reindex(port_rets.index).fillna(0.0)

        equity = (1.0 + net_rets).cumprod()
        return {
            "weights": weights,
            "signal": signals,
            "ranks": ranks,
            "gross_returns": port_rets,
            "transaction_costs": tc,
            "net_returns": net_rets,
            "equity": equity,
        }


