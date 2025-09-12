from __future__ import annotations

import pandas as pd


def cross_sectional_rank(signals: pd.DataFrame) -> pd.DataFrame:
    return signals.rank(axis=1, method="first", na_option="keep", ascending=False)


