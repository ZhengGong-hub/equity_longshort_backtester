from __future__ import annotations

from dataclasses import dataclass
import pandas as pd

from academic_data_download.db_manager.wrds_sql import get_sp500_constituents_snapshot, get_crsp_daily_by_permno_by_year
from academic_data_download.utils.wrds_connect import connect_wrds
import os
import dotenv
import warnings

warnings.filterwarnings("ignore")
dotenv.load_dotenv()


@dataclass
class SP500Universe:
    year: int
    gvkeys: list[str]
    permnos: list[str]

# TODO: implement this
def load_tiny_sample() -> SP500Universe:
    """
    Placeholder tiny dataset loader. Real impl could fetch from wrds.
    """
    pass


def load_sp500_data_wrds(start_year: int, end_year: int) -> dict:
    print("Loading SP500 data...")
    db = connect_wrds(username=os.getenv("WRDS_USERNAME"), password=os.getenv("WRDS_PASSWORD"))

    # get spy 
    spy_daily = get_crsp_daily_by_permno_by_year(db, ["84398"], 'all')
    spy_daily = spy_daily.query(f"date >= '{start_year}-01-01' and date <= '{end_year}-12-31'")
    spy_daily['date'] = pd.to_datetime(spy_daily['date'])
    spy_daily['adjclose'] = spy_daily['prc'] / spy_daily['cfacpr']
    spy_daily['adjopen'] = spy_daily['openprc'] / spy_daily['cfacpr']
    spy_daily['ret_oto'] = spy_daily.groupby('permno')['adjopen'].transform(lambda x: x.pct_change())
    spy_daily['nav'] = (1.0 + spy_daily['ret'].shift(-1)).cumprod()

    sp500_universes = []
    price_df = []
    for year in range(start_year, end_year+1):
        print(f"Loading SP500 data for year {year}...")
        constituents = get_sp500_constituents_snapshot(db, year)[['gvkey', 'permno', 'gsector']]
        print(f"the number of unique permnos for year {year} is {len(constituents['permno'].unique())}")
        print(f"the number of unique gvkeys for year {year} is {len(constituents['gvkey'].unique())}")
        crsp_daily = get_crsp_daily_by_permno_by_year(db, constituents["permno"].unique(), year)
        crsp_daily = pd.merge(crsp_daily, constituents, on="permno", how="left")
        crsp_daily['permno'] = crsp_daily['permno'].astype(str) # convert permno to string for easier querying

        price_df.append(crsp_daily)
        sp500_universes.append(
            SP500Universe(
                year=year, 
                gvkeys=constituents["gvkey"].unique(), 
                permnos=constituents["permno"].unique(), 
                ))
    price_df_long = pd.concat(price_df)
    price_df_long['date'] = pd.to_datetime(price_df_long['date'])
    price_df_long['adjclose'] = price_df_long['prc'] / price_df_long['cfacpr']
    price_df_long['adjopen'] = price_df_long['openprc'] / price_df_long['cfacpr']
    price_df_long['ret_oto'] = price_df_long.groupby('permno')['adjopen'].transform(lambda x: x.pct_change())

    retoto_df_wide = price_df_long.pivot(index="date", columns="permno", values="ret_oto")
    retctc_df_wide = price_df_long.pivot(index="date", columns="permno", values="ret")
    adjclose_df_wide = price_df_long.pivot(index="date", columns="permno", values="adjclose")
    adjopen_df_wide = price_df_long.pivot(index="date", columns="permno", values="adjopen")
    sector_df_wide = price_df_long.pivot(index="date", columns="permno", values="gsector")

    # final ffill 
    retoto_df_wide = retoto_df_wide.ffill(limit = 5)
    retctc_df_wide = retctc_df_wide.ffill(limit = 5)
    adjclose_df_wide = adjclose_df_wide.ffill(limit = 5)
    adjopen_df_wide = adjopen_df_wide.ffill(limit = 5)
    sector_df_wide = sector_df_wide.ffill(limit = 5)

    return {
        "sp500_universes": sp500_universes,
        
        # long format
        "price_df_long": price_df_long,

        # wide format: return, open-to-open, close-to-close
        "retoto_df_wide": retoto_df_wide,
        "retctc_df_wide": retctc_df_wide,

        # wide format: price adjusted
        "adjclose_df_wide": adjclose_df_wide,
        "adjopen_df_wide": adjopen_df_wide,
        # wide format: sector
        "sector_df_wide": sector_df_wide,

        # supportive data 
        "spy_daily": spy_daily
    }
