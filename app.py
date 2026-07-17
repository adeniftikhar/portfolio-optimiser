import streamlit as st
import pandas as pd
import numpy as np
import cvxpy as cp
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Portfolio Optimiser", layout="wide")

RISK_FREE_RATE = 0.04
MAX_WEIGHT = 0.40

@st.cache_data
def load_data():
    expected_returns = pd.read_csv("data/expected_returns.csv", index_col=0).iloc[:, 0]
    cov_matrix = pd.read_csv("data/cov_matrix.csv", index_col=0)
    prices = pd.read_csv("data/combined_prices.csv", index_col=0, parse_dates=True)
    return expected_returns, cov_matrix, prices

expected_returns, cov_matrix, prices = load_data()
tickers = expected_returns.index.tolist()
mu = expected_returns.values
Sigma = cov_matrix.values
n = len(tickers)

@st.cache_data
def build_frontier():
    target_returns = np.linspace(mu.min(), mu.max(), 50)
    frontier = []
    for target in target_returns:
        w = cp.Variable(n)
        constraints = [cp.sum(w) == 1, w >= 0, w <= MAX_WEIGHT, mu @ w >= target]
        problem = cp.Problem(cp.Minimize(cp.quad_form(w, Sigma)), constraints)
        problem.solve()
        if problem.status != "optimal":
            continue
        weights = w.value
        port_return = weights @ mu
        port_vol = np.sqrt(weights @ Sigma @ weights)
        sharpe = (port_return - RISK_FREE_RATE) / port_vol
        frontier.append({"weights": weights, "return": port_return,
                          "volatility": port_vol, "sharpe": sharpe})
    return frontier

frontier = build_frontier()

# --- Sidebar: user inputs from the document's Step 9 ---
st.sidebar.header("Your details")
investment = st.sidebar.number_input("Investment amount (£)", min_value=100, value=10000, step=500)
risk_tolerance = st.sidebar.select_slider("Risk tolerance", options=["Low", "Medium", "High"], value="Medium")
horizon = st.sidebar.slider("Investment horizon (years)", 1, 20, 5)

risk_to_max_vol = {"Low": 0.10, "Medium": 0.20, "High": 0.35}
max_vol = risk_to_max_vol[risk_tolerance]

eligible = [p for p in frontier if p["volatility"] <= max_vol]
recommended = max(eligible, key=lambda p: p["return"]) if eligible else min(frontier, key=lambda p: p["volatility"])

# --- Main page ---
st.title("Portfolio Optimisation Tool")
st.caption("Based on Modern Portfolio Theory and historical data. Not financial advice.")

col1, col2, col3 = st.columns(3)
col1.metric("Expected annual return", f"{recommended['return']:.1%}")
col2.metric("Expected annual volatility", f"{recommended['volatility']:.1%}")
col3.metric("Sharpe ratio", f"{recommended['sharpe']:.2f}")

st.subheader("Recommended allocation")
weights_series = pd.Series(recommended["weights"], index=tickers)
weights_series = weights_series[weights_series > 0.001]
st.plotly_chart(px.pie(values=weights_series.values, names=weights_series.index, hole=0.4),
                 use_container_width=True)

st.subheader("Efficient frontier")
frontier_df = pd.DataFrame([{"return": p["return"], "volatility": p["volatility"]} for p in frontier])
fig_frontier = go.Figure()
fig_frontier.add_trace(go.Scatter(x=frontier_df["volatility"], y=frontier_df["return"],
                                   mode="lines", name="Efficient frontier"))
fig_frontier.add_trace(go.Scatter(x=[recommended["volatility"]], y=[recommended["return"]],
                                   mode="markers", marker=dict(size=14, color="red"),
                                   name="Your portfolio"))
fig_frontier.update_layout(xaxis_title="Volatility (risk)", yaxis_title="Expected return")
st.plotly_chart(fig_frontier, use_container_width=True)

st.subheader("Correlation between assets")
corr = prices.pct_change().dropna().corr()
st.plotly_chart(px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1),
                 use_container_width=True)

st.subheader("How this allocation would have performed historically")
daily_returns = prices.pct_change().dropna()
portfolio_daily_returns = daily_returns[tickers] @ recommended["weights"]
growth = investment * (1 + portfolio_daily_returns).cumprod()
st.line_chart(growth)