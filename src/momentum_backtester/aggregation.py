from __future__ import annotations

import pandas as pd


def long_short_top_bottom(
    ranks: pd.DataFrame,
    sectors: pd.DataFrame,
    top_n: int = 50,
    bottom_n: int = 50,
) -> pd.DataFrame:
    weights = pd.DataFrame(0.0, index=ranks.index, columns=ranks.columns)
    for date, row in ranks.iterrows():
        valid = row.dropna()
        if valid.empty:
            continue
        top = valid.nsmallest(top_n)
        bot = valid.nlargest(bottom_n)
        w = pd.Series(0.0, index=row.index)
        if len(top) > 0:
            w.loc[top.index] = 1.0 / len(top)
        if len(bot) > 0:
            w.loc[bot.index] = -1.0 / len(bot)
        weights.loc[date] = w
    return weights


