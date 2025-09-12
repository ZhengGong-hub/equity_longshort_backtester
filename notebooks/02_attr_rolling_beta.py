# %% [markdown]
# Rolling beta (placeholder)

# %%
import pandas as pd
from momentum_backtester.metrics import volatility

series = pd.Series([0.0, 0.01, -0.005, 0.002])
volatility(series)


