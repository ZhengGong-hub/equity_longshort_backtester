from __future__ import annotations

from dataclasses import dataclass
import pandas as pd


@dataclass
class SP500Universe:
    prices: pd.DataFrame
    sectors: pd.DataFrame
    universe: pd.DataFrame


def load_tiny_sample() -> SP500Universe:
    """Placeholder tiny dataset loader. Real impl could fetch from GitHub.

    For tests, we expect CSVs in tests/data.
    """
    base = "tests/data"
    prices = pd.read_csv(f"{base}/tiny_prices.csv", parse_dates=[0], index_col=0)
    sectors = pd.read_csv(f"{base}/tiny_sectors.csv", index_col=0)
    universe = pd.read_csv(f"{base}/tiny_universe.csv", index_col=0)
    return SP500Universe(prices=prices, sectors=sectors, universe=universe)


