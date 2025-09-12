from __future__ import annotations

import pandas as pd


def turnover_costs(weights: pd.DataFrame, bps_per_turnover: float = 10.0) -> pd.Series:
    """Linear costs: bps per 100% turnover, charged on rebalance dates.

    Returns Series indexed by dates.
    """
    w = weights.fillna(0.0)
    tw = w.diff().abs().sum(axis=1).fillna(0.0)
    daily_cost = (bps_per_turnover / 10000.0) * (tw / 2.0)
    return daily_cost


