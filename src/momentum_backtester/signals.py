from __future__ import annotations

import pandas as pd


def close_to_close_momentum(prices: pd.DataFrame, lookback_days: int = 252, skip: int = 1) -> pd.DataFrame:
    """Simple price momentum using close-to-close total return over lookback minus skip.

    Returns a DataFrame aligned with `prices` index/columns with momentum values.
    """
    ret = prices.pct_change(lookback_days)

    if skip > 0:
        ret = ret.shift(skip)
    return ret.reindex(prices.index).ffill()


