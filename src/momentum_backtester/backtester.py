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


@dataclass
class BacktestConfig:
    rebalance: str = "M"  # month-end
    top_n: int = 50
    bottom_n: int = 50
    long_short: bool = True


class Backtester:
    def __init__(
        self,
        prices: pd.DataFrame,
        sectors: pd.DataFrame,
        universe: pd.DataFrame,
        signal: SignalFunc,
        ranker: RankFunc,
        aggregator: AggFunc,
        costs: CostFunc,
        config: BacktestConfig | None = None,
    ) -> None:
        self.prices = prices.sort_index()
        self.sectors = sectors
        self.universe = universe
        self.signal = signal
        self.ranker = ranker
        self.aggregator = aggregator
        self.costs = costs
        self.config = config or BacktestConfig()
        self.calendar = MonthEndCalendar()

    def run(self) -> Dict[str, pd.DataFrame | pd.Series]:
        px = self.prices.loc[:, self.prices.columns.intersection(self.universe.columns)]
        px = px.ffill()
        rebal_dates = self.calendar.month_ends(px.index)

        signals = self.signal(px)
        ranks = self.ranker(signals.loc[rebal_dates])

        weights = self.aggregator(ranks, self.sectors)
        weights = weights.reindex(rebal_dates).fillna(0.0)

        rets = px.pct_change().fillna(0.0)
        port_rets = (weights.shift().reindex(rets.index).fillna(0.0) * rets).sum(axis=1)

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


