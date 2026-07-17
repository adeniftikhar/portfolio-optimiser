import yfinance as yf
import os

# A small, diversified set of assets across asset classes
tickers = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "Nvidia",
    "VOO": "S&P 500 ETF",
    "GLD": "Gold ETF",
    "IEF": "US Treasury Bond ETF (7-10yr)",
    "BTC-USD": "Bitcoin",
}

start_date = "2015-01-01"

os.makedirs("data", exist_ok=True)

for ticker, name in tickers.items():
    print(f"Downloading {ticker} ({name})...")
    try:
        df = yf.download(ticker, start=start_date, auto_adjust=True, progress=False)
        df.columns = df.columns.get_level_values(0)
        if df.empty:
            print(f"  WARNING: no data returned for {ticker}")
            continue
        df.to_csv(f"data/{ticker}.csv")
        print(f"  Saved {len(df)} rows to data/{ticker}.csv")
    except Exception as e:
        print(f"  ERROR downloading {ticker}: {e}")

print("Done.")