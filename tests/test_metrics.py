from __future__ import annotations

import pandas as pd
from momentum_backtester.metrics import cagr, volatility, sharpe, max_drawdown


def test_metrics_basic():
    r = pd.Series([0.01] * 252)
    assert cagr(r) > 0
    assert volatility(r) >= 0
    assert sharpe(r) > 0
    assert max_drawdown(r) <= 0


