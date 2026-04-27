"""
app.py
Streamlit dashboard for energy market regime change detection.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from regime_detector import SYMBOLS, run_analysis

# ---- Page config ----
st.set_page_config(
    page_title="Energy Regime Detector",
    page_icon="📊",
    layout="wide",
)

# ---- Sidebar ----
st.sidebar.title("Configuration")

symbol_name = st.sidebar.selectbox(
    "Commodity",
    list(SYMBOLS.keys()),
    index=0,
)
symbol = SYMBOLS[symbol_name]

years = st.sidebar.slider("History (years)", 1, 10, 5)

window = st.sidebar.slider("Rolling window (trading days)", 5, 63, 21)

alert_threshold = st.sidebar.slider("Stress alert threshold", 0.5, 0.95, 0.7, 0.05)

# ---- Run analysis ----
with st.spinner(f"Fetching {symbol_name} data and fitting model..."):
    try:
        result = run_analysis(symbol, years, window)
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

# ---- Header ----
st.title("Energy Market Regime Detector")
st.caption(
    "Computes rolling log-return volatility on energy futures and uses a "
    "two-state Hidden Markov Model to classify the market as calm or stress."
)

# ---- Regime gauge ----
col1, col2, col3, col4 = st.columns(4)

stress_pct = result["current_stress_prob"] * 100
current_vol_pct = result["current_vol"] * 100

with col1:
    regime_color = "🔴" if result["current_regime"] == "STRESS" else "🟢"
    st.metric("Current regime", f"{regime_color} {result['current_regime']}")

with col2:
    st.metric("Stress probability", f"{stress_pct:.1f}%")

with col3:
    st.metric("Current annualized vol", f"{current_vol_pct:.1f}%")

with col4:
    calm_vol = result["calm_mean_vol"] * 100
    stress_vol = result["stress_mean_vol"] * 100
    st.metric("Calm / Stress avg vol", f"{calm_vol:.1f}% / {stress_vol:.1f}%")

# ---- Alert ----
if result["current_stress_prob"] >= alert_threshold:
    st.error(
        f"⚠️ REGIME ALERT: Stress probability is {stress_pct:.1f}%, "
        f"above the {alert_threshold*100:.0f}% threshold. "
        f"Current annualized vol: {current_vol_pct:.1f}%."
    )

# ---- Charts ----

# 1. Price + regime overlay
fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.04,
    row_heights=[0.4, 0.3, 0.3],
    subplot_titles=[
        f"{symbol_name} close price",
        f"Rolling {window}-day annualized volatility",
        "Regime stress probability",
    ],
)

# Price chart
fig.add_trace(
    go.Scatter(
        x=result["prices"].index,
        y=result["prices"]["Close"],
        name="Price",
        line=dict(color="#A39B92", width=1),
    ),
    row=1, col=1,
)

# Color background by regime
states = result["regime"]["states"]
stress_state = result["regime"]["stress_state"]

# Add red shading for stress periods
stress_mask = states == stress_state
if stress_mask.any():
    # Find contiguous stress blocks
    diff = stress_mask.astype(int).diff().fillna(0)
    starts = states.index[diff == 1].tolist()
    ends = states.index[diff == -1].tolist()

    # Handle edge cases
    if stress_mask.iloc[0]:
        starts.insert(0, states.index[0])
    if stress_mask.iloc[-1]:
        ends.append(states.index[-1])

    for s, e in zip(starts, ends):
        fig.add_vrect(
            x0=s, x1=e,
            fillcolor="rgba(148, 58, 58, 0.15)",
            layer="below",
            line_width=0,
            row=1, col=1,
        )
        fig.add_vrect(
            x0=s, x1=e,
            fillcolor="rgba(148, 58, 58, 0.15)",
            layer="below",
            line_width=0,
            row=2, col=1,
        )

# Volatility chart
vol = result["volatility"].dropna()
fig.add_trace(
    go.Scatter(
        x=vol.index,
        y=vol.values * 100,
        name="Annualized vol (%)",
        line=dict(color="#4A7C5C", width=1.5),
    ),
    row=2, col=1,
)

# Horizontal lines for calm/stress mean vol
fig.add_hline(
    y=result["calm_mean_vol"] * 100,
    line_dash="dot",
    line_color="#4A7C5C",
    annotation_text=f"Calm avg: {result['calm_mean_vol']*100:.1f}%",
    row=2, col=1,
)
fig.add_hline(
    y=result["stress_mean_vol"] * 100,
    line_dash="dot",
    line_color="#943A3A",
    annotation_text=f"Stress avg: {result['stress_mean_vol']*100:.1f}%",
    row=2, col=1,
)

# Changepoint markers
for cp in result["changepoints"]:
    if cp in vol.index:
        fig.add_vline(
            x=cp,
            line_dash="dash",
            line_color="#C9A87C",
            line_width=1,
            row=2, col=1,
        )

# Stress probability chart
stress_prob = result["regime"]["stress_prob"]
fig.add_trace(
    go.Scatter(
        x=stress_prob.index,
        y=stress_prob.values * 100,
        name="Stress probability (%)",
        fill="tozeroy",
        fillcolor="rgba(148, 58, 58, 0.2)",
        line=dict(color="#943A3A", width=1.5),
    ),
    row=3, col=1,
)

# Threshold line
fig.add_hline(
    y=alert_threshold * 100,
    line_dash="dash",
    line_color="#A39B92",
    annotation_text=f"Alert: {alert_threshold*100:.0f}%",
    row=3, col=1,
)

# Layout
fig.update_layout(
    height=800,
    showlegend=False,
    template="plotly_dark",
    paper_bgcolor="#1A1A1D",
    plot_bgcolor="#222225",
    font=dict(family="Outfit, sans-serif", color="#CCC5BB"),
    margin=dict(l=60, r=20, t=40, b=40),
)

fig.update_xaxes(gridcolor="#333336")
fig.update_yaxes(gridcolor="#333336")

st.plotly_chart(fig, use_container_width=True)

# ---- Methodology ----
with st.expander("Methodology"):
    st.markdown("""
**Log returns:** Daily log returns are computed as ln(P_t / P_{t-1}).

**Rolling volatility:** Standard deviation of log returns over the rolling
window, annualized by multiplying by √252 (trading days per year).

**Regime classification:** A two-state Gaussian Hidden Markov Model is fit
to the volatility series. The model identifies two distributions (calm and stress)
and computes the probability of being in each state at every time step.

**Changepoint detection:** The PELT algorithm (Pruned Exact Linear Time) from
the `ruptures` library identifies structural breaks in the volatility series,
marking points where the statistical properties of the data change.

**Alert threshold:** When the stress probability exceeds the configured threshold,
the dashboard fires an alert. In backtesting, this detector would have flagged
the February 2022 vol regime shift within the first trading sessions.
    """)

# ---- Footer ----
st.caption("Built by Gaby Hernandez | gabyhernandez.dev")
