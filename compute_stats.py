import pandas as pd
import numpy as np
import os

tickers = ["AAPL", "MSFT", "NVDA", "VOO", "GLD", "IEF", "BTC-USD"]

# Load each CSV and pull out just the Close column
price_data = {}
for ticker in tickers:
    path = f"data/{ticker}.csv"
    if not os.path.exists(path):
        print(f"WARNING: {path} not found, skipping")
        continue
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    price_data[ticker] = df["Close"]

prices = pd.DataFrame(price_data)

# Align dates - some assets trade different days (crypto vs stocks),
# so drop any row where at least one asset is missing a price
prices = prices.dropna()

print(f"Combined price table: {prices.shape[0]} rows, {prices.shape[1]} assets")
prices.to_csv("data/combined_prices.csv")

# Daily returns (percentage change day to day)
daily_returns = prices.pct_change().dropna()

# Annualise: 252 is the standard number of trading days in a year
expected_returns = daily_returns.mean() * 252
volatility = daily_returns.std() * np.sqrt(252)
cov_matrix = daily_returns.cov() * 252
corr_matrix = daily_returns.corr()

print("\nExpected annual returns:")
print(expected_returns.round(3))

print("\nAnnual volatility:")
print(volatility.round(3))

print("\nCorrelation matrix:")
print(corr_matrix.round(2))

# Save for step 4 (the optimiser)
expected_returns.to_csv("data/expected_returns.csv")
cov_matrix.to_csv("data/cov_matrix.csv")

