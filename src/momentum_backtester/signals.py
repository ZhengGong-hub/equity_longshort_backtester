from __future__ import annotations

import pandas as pd


def price_momentum(
    prices: pd.DataFrame,
    lookback_months: int = 11,
    skip: int = 1,
) -> pd.DataFrame:
    """
    Compute simple close-to-close momentum.

    Momentum_t = (Price_{t-skip} / Price_{t-skip-lookback}) - 1

    Parameters
    ----------
    prices : pd.DataFrame
        Wide DataFrame of prices, index must be a DatetimeIndex, columns = tickers.
    lookback_days : int, default 252
        Lookback window length in trading days (≈12 months).
    skip : int, default 1
        Number of most recent observations to skip (skip=1 implements 12-1 momentum).

    Returns
    -------
    pd.DataFrame
        Momentum values aligned with `prices` (same index and columns).
    """
    lookback_days = lookback_months * 21
    skip_days = skip * 21

    # Shifted prices
    p_t1 = prices.shift(skip_days)                     # Price at t-skip
    p_tL = prices.shift(skip_days + lookback_days)     # Price at t-skip-lookback

    mom = ((p_t1 / p_tL) - 1.0).shift(1) # to avoid future leakage

    # Align exactly to original index/columns
    return mom.reindex(prices.index).ffill()