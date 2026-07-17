import cvxpy as cp
import numpy as np
import pandas as pd

# Load the stats from step 3
expected_returns = pd.read_csv("data/expected_returns.csv", index_col=0).iloc[:, 0]
cov_matrix = pd.read_csv("data/cov_matrix.csv", index_col=0)

tickers = expected_returns.index.tolist()
n = len(tickers)
mu = expected_returns.values
Sigma = cov_matrix.values

RISK_FREE_RATE = 0.04   # rough approximation of a risk-free return, used in the Sharpe ratio
MAX_WEIGHT = 0.40        # no single asset can exceed 40% of the portfolio

def solve_portfolio(target_return=None):
    """Find the minimum-variance portfolio, optionally constrained to
    hit at least a given target return. Sweeping target_return across
    a range traces out the efficient frontier."""
    w = cp.Variable(n)
    portfolio_variance = cp.quad_form(w, Sigma)

    constraints = [
        cp.sum(w) == 1,   # fully invested, weights sum to 100%
        w >= 0,           # no short selling
        w <= MAX_WEIGHT,  # no single asset dominating
    ]
    if target_return is not None:
        constraints.append(mu @ w >= target_return)

    problem = cp.Problem(cp.Minimize(portfolio_variance), constraints)
    problem.solve()

    return w.value if problem.status == "optimal" else None



# Trace the efficient frontier by solving many times across a range of target returns
target_returns = np.linspace(mu.min(), mu.max(), 50)

frontier = []
for target in target_returns:
    weights = solve_portfolio(target_return=target)
    if weights is None:
        continue
    port_return = weights @ mu
    port_vol = np.sqrt(weights @ Sigma @ weights)
    sharpe = (port_return - RISK_FREE_RATE) / port_vol
    frontier.append({"weights": weights, "return": port_return,
                      "volatility": port_vol, "sharpe": sharpe})



min_var_portfolio = min(frontier, key=lambda p: p["volatility"])
max_sharpe_portfolio = max(frontier, key=lambda p: p["sharpe"])

def print_portfolio(name, portfolio):
    print(f"\n{name}")
    print(f"  Expected return: {portfolio['return']:.3f}")
    print(f"  Volatility:      {portfolio['volatility']:.3f}")
    print(f"  Sharpe ratio:    {portfolio['sharpe']:.3f}")
    for ticker, weight in zip(tickers, portfolio["weights"]):
        if weight > 0.001:
            print(f"    {ticker}: {weight:.1%}")

print_portfolio("Minimum Variance Portfolio", min_var_portfolio)
print_portfolio("Maximum Sharpe Ratio Portfolio", max_sharpe_portfolio)

# Save results for the next step (plotting / Streamlit)
pd.DataFrame([{"return": p["return"], "volatility": p["volatility"], "sharpe": p["sharpe"]}
              for p in frontier]).to_csv("data/efficient_frontier.csv", index=False)
pd.Series(max_sharpe_portfolio["weights"], index=tickers).to_csv("data/max_sharpe_weights.csv")
pd.Series(min_var_portfolio["weights"], index=tickers).to_csv("data/min_var_weights.csv")