from __future__ import annotations

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import warnings
warnings.filterwarnings("ignore")

class Analysis:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def cagr(self, returns: pd.Series, periods_per_year: int = 252) -> float:
        r = returns.dropna()
        if r.empty:
            return 0.0
        total_return = (1.0 + r).prod()
        years = len(r) / periods_per_year
        if years <= 0:
            return 0.0
        cagr = round(total_return ** (1.0 / years) - 1.0, 4)
        print("the CAGR is: ", cagr)
        return cagr

    def annual_vol(self, returns: pd.Series, periods_per_year: int = 252, verbose: bool = True) -> float:
        r = returns.dropna()
        if r.empty:
            return 0.0
        vol = round(r.std() * np.sqrt(periods_per_year), 4)
        if verbose:
            print("the annual volatility is: ", vol)
        return vol

    def sharpe(self, returns: pd.Series, risk_free: float = 0.0, periods_per_year: int = 252) -> float:
        r = returns.dropna() - risk_free / periods_per_year
        vol = self.annual_vol(r, periods_per_year, verbose=False)
        if vol == 0:
            return np.nan
        sharpe = round(r.sum() / vol, 4)
        print("the Sharpe ratio is: ", sharpe)
        return sharpe

    def max_drawdown(self, returns: pd.Series) -> float:
        equity = (1.0 + returns.fillna(0.0)).cumprod()
        rolling_max = equity.cummax()
        drawdown = equity / rolling_max - 1.0
        max_drawdown = round(float(drawdown.min()), 4)
        print("the maximum drawdown is: ", max_drawdown)
        return max_drawdown

    def nav_chart(
        self,
        gross_returns: pd.Series, 
        net_returns: pd.Series,
        incl_spy: bool = False,
        spy_daily: pd.DataFrame = None,
    ) -> None:
        gross_equity = (1.0 + gross_returns.fillna(0.0)).cumprod()
        net_equity = (1.0 + net_returns.fillna(0.0)).cumprod()

        # Compute drawdown for net returns
        rolling_max = net_equity.cummax()
        drawdown = net_equity / rolling_max - 1.0

        fig, (ax1, ax2) = plt.subplots(
            2, 1, figsize=(12, 8), sharex=True, 
            gridspec_kw={'height_ratios': [3, 1]}
        )

        # NAV chart
        ax1.plot(gross_equity, label="Gross Returns")
        ax1.plot(net_equity, label="Net Returns")
        if incl_spy:
            ax1.plot(spy_daily['date'], spy_daily['nav'], label="SPY")
        ax1.set_title("NAV Chart")
        ax1.set_ylabel("Cumulative Return")
        ax1.legend()
        ax1.grid(True, linestyle="--", alpha=0.5)

        # Drawdown chart
        ax2.plot(drawdown, color="red", label="Drawdown (Net)")
        ax2.set_ylabel("Drawdown")
        ax2.set_xlabel("Date")
        ax2.set_title("Drawdown")
        ax2.legend()
        ax2.grid(True, linestyle="--", alpha=0.5)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "nav_chart.png"))

    def spy_chart(self, spy_daily: pd.DataFrame) -> None:
        plt.figure(figsize=(10, 6))
        plt.plot(spy_daily['date'], spy_daily['adjclose'])
        plt.title("SPY Chart")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.savefig(os.path.join(self.output_dir, "spy_chart.png"))

    
    def against_spy(
        self,
        net_returns: pd.Series,
        spy_daily: pd.DataFrame,
        verbose: bool = True,
    ) -> dict:
        # 1) Align on the intersection of dates
        df = pd.concat(
            {
                "y": pd.to_numeric(net_returns, errors="coerce"),
                "m": pd.to_numeric(spy_daily.set_index('date')['ret'].shift(-1), errors="coerce"),
            },
            axis=1,
        )

        # 2) Drop non-numeric / NA and infinities
        df = df.replace({pd.NA: np.nan}).astype(float).replace([np.inf, -np.inf], np.nan).dropna()

        # 3) Build design matrix with intercept as raw numpy (ensures float64)
        X = sm.add_constant(df["m"].to_numpy(dtype=float))
        y = df["y"].to_numpy(dtype=float)

        model = sm.OLS(y, X).fit()
        alpha_m, beta = model.params  # alpha is per-period intercept

        # 4) Annualize alpha depending on frequency
        alpha_annual = alpha_m * 252.0    

        res_dict = {
            "alpha_annual": round(float(alpha_annual), 4),
            "beta": round(float(beta), 4),
            "alpha_per_period": round(float(alpha_m), 4),
            "r2": round(float(model.rsquared), 4),
            # "n": int(len(df)),
        }
        if verbose:
            print(res_dict)
        return res_dict
        
    def rolling_beta(
            self,
            net_returns: pd.Series, 
            spy_daily: pd.DataFrame, 
            window: int = 252,
        ) -> None:
        """

        """
        df = pd.concat({"strat": net_returns, "mkt": spy_daily.set_index('date')['ret'].shift(-1)}, axis=1).dropna()
        cov = df["strat"].rolling(window).cov(df["mkt"])
        var = df["mkt"].rolling(window).var()
        beta = cov / var

        # Plot
        plt.figure(figsize=(10,5))
        beta.plot(color="navy", lw=2, label="12-month rolling beta")
        plt.title("Rolling Beta of Strategy vs S&P 500")
        plt.xlabel("Date")
        plt.ylabel("Beta")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.savefig(os.path.join(self.output_dir, "rolling_beta.png"))
    

    def return_attr_sector(
        self,
        weights: pd.DataFrame,
        sector_df_wide: pd.DataFrame,
        retoto_df_wide: pd.DataFrame,
        gross_returns: pd.Series,
        verbose: bool = True,
    ) -> None:
        """
        Compute return attribution by sector.

        Here i use the arithematic sum to compute the sector return. 
        So the sector return summation align with the arithmetic sum of the gross return, not compounding.
        """
        w_ret = weights * (retoto_df_wide.shift(-1))

        sector_date = sector_df_wide.loc[w_ret.index[0]]
        sector_stats = sector_date.value_counts()
        sector_ret_df = pd.DataFrame(index=w_ret.index, columns=sector_stats.index)

        for date, row in w_ret.iterrows():
            valid = row.dropna()
            if valid.empty:
                continue
            
            for sector in sector_stats.index:
                valid_names = valid[sector_date == sector]
                # sector_ret is sum up
                sector_ret = valid_names.sum()
                # print("sector_ret of sector: ", sector, " is: ", sector_ret)
                sector_ret_df.loc[date][sector] = sector_ret
        
        sector_ret_df['-gross_ret'] = -gross_returns
        sector_ret_df['check_sum'] = sector_ret_df.sum(axis=1) # just as an internal note, this column should be 0 at any date
        # print(sector_ret_df)

        total_sector_ret_df = sector_ret_df.sum(axis=0)
        if verbose:
            print(total_sector_ret_df)
        return total_sector_ret_df


    def total_turnover(
        self,
        weights: pd.DataFrame,
        verbose: bool = True,
    ) -> pd.Series:
        """
        Compute total turnover.
        """
        total_turnover = weights.diff().abs().sum(axis=1).fillna(0.0)
        
        # plot the total turnover
        plt.figure(figsize=(10,5))
        total_turnover.plot(color="navy", lw=2, label="Total Turnover")
        plt.title("Total Turnover")
        plt.xlabel("Date")
        plt.ylabel("Turnover")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.savefig(os.path.join(self.output_dir, "total_turnover.png"))

        total_turnover_per_annum = total_turnover.resample('Y').sum()
        if verbose:
            print("the total turnover per annum is: ", total_turnover_per_annum)
        return total_turnover_per_annum
