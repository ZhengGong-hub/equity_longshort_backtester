from __future__ import annotations

import numpy as np
import pandas as pd


def cagr(returns: pd.Series, periods_per_year: int = 252) -> float:
    r = returns.dropna()
    if r.empty:
        return 0.0
    total_return = (1.0 + r).prod()
    years = len(r) / periods_per_year
    if years <= 0:
        return 0.0
    return total_return ** (1.0 / years) - 1.0


def volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
    r = returns.dropna()
    if r.empty:
        return 0.0
    return r.std() * np.sqrt(periods_per_year)


def sharpe(returns: pd.Series, risk_free: float = 0.0, periods_per_year: int = 252) -> float:
    r = returns.dropna() - risk_free / periods_per_year
    vol = volatility(r, periods_per_year)
    if vol == 0:
        return 0.0
    return r.mean() * periods_per_year / vol


def max_drawdown(returns: pd.Series) -> float:
    equity = (1.0 + returns.fillna(0.0)).cumprod()
    rolling_max = equity.cummax()
    drawdown = equity / rolling_max - 1.0
    return float(drawdown.min())


