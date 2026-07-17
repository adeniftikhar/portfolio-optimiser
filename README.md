# Portfolio Optimiser

A Python tool that builds data-driven investment portfolios using **Modern Portfolio Theory (MPT)**. Given a risk tolerance and investment amount, it recommends an asset allocation calculated from real historical market data rather than a set of arbitrary percentages.

**Live app:** (https://aden-portfolio-optimiser.streamlit.app/)

> This project is for educational purposes only. It is not financial advice.

---

## What it does

The app answers a practical question: *given my goals and risk tolerance, how should I invest?*

It does this by:
1. Downloading historical price data for a diversified set of assets
2. Calculating each asset's expected return, volatility, and how they move relative to one another (correlation)
3. Using convex optimisation to solve for the portfolio that minimises risk for a given target return, across a full range of targets — tracing out the **efficient frontier**
4. Mapping the user's risk tolerance to a maximum acceptable volatility, and recommending the highest-return portfolio on the frontier that stays within it
5. Visualising the result: allocation breakdown, the efficient frontier itself, a correlation heatmap, and a historical backtest of how that allocation would have performed

---

## Tech stack

| Purpose | Tool |
|---|---|
| Data collection | [yfinance](https://github.com/ranaroussi/yfinance) |
| Data handling | pandas, numpy |
| Portfolio optimisation | [CVXPY](https://www.cvxpy.org/) |
| Charts | Plotly |
| Web app / UI | [Streamlit](https://streamlit.io/) |
| Deployment | Streamlit Community Cloud |

Everything used is free and open source.

---

## Assets covered

| Ticker | Asset | Role in the portfolio |
|---|---|---|
| AAPL | Apple | Individual growth stock |
| MSFT | Microsoft | Individual growth stock |
| NVDA | Nvidia | High-growth, high-volatility stock |
| VOO | S&P 500 ETF | Broad market exposure |
| GLD | Gold ETF | Diversifier, low correlation to equities |
| IEF | 7–10yr US Treasury Bond ETF | Diversifier, negatively correlated to equities |
| BTC-USD | Bitcoin | High-growth, high-volatility, weakly correlated to equities |

This mix was chosen deliberately to span different asset classes rather than just picking well-known stocks — the diversification benefit in Modern Portfolio Theory comes specifically from combining assets that *don't* move together.

---

## The methodology

**1. Returns and risk.** Daily price data is converted to daily returns, then annualised (× 252 trading days for return, × √252 for volatility) to get each asset's expected annual return (μ) and volatility (σ).

**2. Covariance matrix (Σ).** Captures how every pair of assets moves together. This is what allows the optimiser to find diversification benefits that a naive return-only strategy would miss.

**3. Portfolio maths.** For a set of weights `w`:
- Portfolio return: `w^T μ`
- Portfolio variance: `w^T Σ w`

**4. The efficient frontier.** Rather than randomly sampling thousands of portfolios, this project solves a proper constrained optimisation problem with CVXPY for a sweep of target returns: *"of all portfolios that achieve at least this return, which has the lowest variance?"* Solving this repeatedly across the full range of achievable returns traces out the actual mathematical efficient frontier.

**5. Constraints.** Two constraints are applied beyond the basics (weights sum to 100%, no short selling):
- **Maximum 40% in any single asset** — without this, the optimiser tends to concentrate heavily in whichever asset had the best historical risk/return trade-off, which is more a symptom of estimation noise in the covariance matrix than a genuinely robust recommendation.
- **Risk tolerance → maximum volatility** — Low/Medium/High risk tolerance is mapped to a maximum acceptable portfolio volatility (10% / 20% / 35%), and the app recommends the highest-return portfolio on the frontier that respects that cap.

**6. Sharpe ratio.** `(portfolio return − risk-free rate) / portfolio volatility` — used to identify the portfolio with the best return per unit of risk taken, alongside the minimum-variance portfolio.

---

## Known limitations

Being upfront about these is part of the point of the project, not a weakness in it:

- **Estimation sensitivity.** Mean-variance optimisation is highly sensitive to the expected-return inputs specifically — small changes can meaningfully shift the "optimal" portfolio. This is a well-documented critique of Markowitz-style optimisation (see Michaud's "error-maximisation" problem).
- **Past performance ≠ future performance.** Expected returns are calculated purely from historical averages, which are a weak predictor of future returns.
- **Non-normal returns.** Daily returns are not truly normally distributed (they have fatter tails than a normal distribution), so volatility likely understates real tail risk.
- **Constraint choices are judgement calls**, not laws of nature — the 40% cap and the risk-tolerance-to-volatility mapping were both design decisions made for this project, and are worth justifying rather than treating as fixed facts.
- **Data reliability.** Historical price data is sourced via yfinance, an unofficial wrapper around Yahoo Finance rather than a guaranteed API — occasional failures are handled gracefully but are a known constraint of using free data sources.

---

## Project structure

```
portfolio-optimiser/
├── data/                      # Downloaded and computed data (gitignored)
│   ├── AAPL.csv, MSFT.csv...  # Raw price history per asset
│   ├── combined_prices.csv    # Aligned price table across all assets
│   ├── expected_returns.csv
│   ├── cov_matrix.csv
│   ├── efficient_frontier.csv
│   ├── max_sharpe_weights.csv
│   └── min_var_weights.csv
├── fetch_data.py               # Step 1: downloads and cleans historical price data
├── compute_stats.py            # Step 2: calculates returns, volatility, covariance
├── optimize.py                 # Step 3: solves for the efficient frontier via CVXPY
├── app.py                      # Step 4: Streamlit web app
├── requirements.txt
└── README.md
```

---

## Running it locally

```bash
# 1. Clone and enter the project
git clone https://github.com/adeniftikhar/portfolio-optimiser.git
cd portfolio-optimiser

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Fetch data and compute statistics (only needs to be run once, or whenever you want fresh data)
python fetch_data.py
python compute_stats.py

# 5. Launch the app
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`.

---

## Roadmap / stretch goals

- [ ] Monte Carlo simulation of future portfolio value across thousands of possible market paths
- [ ] Stress testing the recommended portfolio against 2008, 2020, and 2022 market conditions
- [ ] Black-Litterman model, blending market equilibrium returns with custom investor views
- [ ] Comparing historical-average return estimates against a simple ML-based prediction, with an honest discussion of why beating the market is hard

---

## Why this project

Most beginner finance/coding projects stop at displaying stock prices or predicting tomorrow's price. This project instead tackles a more grounded question — given a set of goals and constraints, how should money actually be allocated — using the same mathematical framework (Modern Portfolio Theory) that underpins real-world portfolio construction, built from real market data rather than illustrative numbers.