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
        ret_df_wide: pd.DataFrame,
        price_df_wide: pd.DataFrame,
        sector_df_wide: pd.DataFrame,
        signal: SignalFunc,
        ranker: RankFunc,
        aggregator: AggFunc,
        costs: CostFunc,
        rebal_freq: str = "M",
    ) -> None:
        self.ret_df_wide = ret_df_wide.sort_index()
        self.price_df_wide = price_df_wide.sort_index()
        self.sector_df_wide = sector_df_wide.sort_index()
        self.signal = signal
        self.ranker = ranker
        self.aggregator = aggregator
        self.costs = costs
        self.calendar = MonthEndCalendar()
        self.rebal_freq = rebal_freq

    def run(self) -> Dict[str, pd.DataFrame | pd.Series]:
        if self.rebal_freq == "D":
            rebal_dates = self.calendar.day_ends(self.ret_df_wide.index)
        elif self.rebal_freq == "M":
            rebal_dates = self.calendar.month_ends(self.ret_df_wide.index)
        else:
            raise ValueError(f"Invalid rebalance frequency: {self.rebal_freq}")
        # print(rebal_dates)

        signals = self.signal(self.price_df_wide)
        # print(signals.tail())

        ranks = self.ranker(signals.loc[rebal_dates])
        # print(ranks.tail())

        weights = self.aggregator(ranks, self.sector_df_wide)
        weights = weights.reindex(rebal_dates).fillna(0.0)

        port_rets = (weights.shift().reindex(self.ret_df_wide.index).fillna(0.0) * self.ret_df_wide).sum(axis=1)

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


