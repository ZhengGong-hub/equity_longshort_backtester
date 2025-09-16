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


def long_short_top_bottom_sector_neutral(
    ranks: pd.DataFrame,
    sectors: pd.DataFrame,
    top_pctg: int = 20,
    bottom_pctg: int = 20,
) -> pd.DataFrame:
    """
    Construct a sector-neutral long-short portfolio by selecting the top and bottom
    percentage of stocks within each sector based on their cross-sectional ranks.

    For each date:
        - Within each sector, select the top `top_pctg` percent (lowest rank values)
          and bottom `bottom_pctg` percent (highest rank values) of stocks.
        - Assign equal positive weights to the top stocks and equal negative weights
          to the bottom stocks, such that the sum of long and short weights are each
          normalized to 1 and -1, respectively, across all selected stocks.
        - Stocks not in the top or bottom groups receive zero weight.
        - The process is repeated independently for each sector, ensuring sector neutrality.
    """
    weights = pd.DataFrame(0.0, index=ranks.index, columns=ranks.columns)
    for date, row in ranks.iterrows():
        valid = row.dropna()
        if valid.empty:
            continue
        w = pd.Series(0.0, index=row.index)

        sector_date = sectors.loc[date]

        sector_stats = sector_date.value_counts()
        sector_list = sector_stats.index

        top, bot = [], []
        for sector in sector_list:
            valid_names = valid[sector_date == sector]

            nsmallest = int(top_pctg/100 * len(valid_names))
            nlargest = int(bottom_pctg/100 * len(valid_names))

            top.append(valid_names.nsmallest(nsmallest))
            bot.append(valid_names.nlargest(nlargest))

        top = pd.concat(top)
        bot = pd.concat(bot)

        if len(top) > 0:
            w.loc[top.index] = 1.0 / len(top)
        if len(bot) > 0:
            w.loc[bot.index] = -1.0 / len(bot)
        weights.loc[date] = w

    return weights


def long_only(
    ranks: pd.DataFrame,
    sectors: pd.DataFrame,
    top_pctg: int = 20,
) -> pd.DataFrame:
    weights = pd.DataFrame(0.0, index=ranks.index, columns=ranks.columns)
    for date, row in ranks.iterrows():
        valid = row.dropna()
        if valid.empty:
            continue
        w = pd.Series(0.0, index=row.index)

        sector_date = sectors.loc[date]
        sector_stats = sector_date.value_counts()

        top = []
        for sector in sector_stats.index:
            valid_names = valid[sector_date == sector]

            nsmallest = int(top_pctg/100 * len(valid_names))

            top.append(valid_names.nsmallest(nsmallest))

        top = pd.concat(top)

        if len(top) > 0:
            w.loc[top.index] = 1.0 / len(top)
        weights.loc[date] = w

    return weights
