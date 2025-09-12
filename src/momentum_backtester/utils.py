from __future__ import annotations

import pandas as pd


class MonthEndCalendar:
    def month_ends(self, index: pd.Index) -> pd.DatetimeIndex:
        if not isinstance(index, pd.DatetimeIndex):
            index = pd.DatetimeIndex(index)
        month_end_flags = index.to_series().groupby([index.year, index.month]).tail(1)
        return pd.DatetimeIndex(month_end_flags.index)


