"""
app.py
Energy Market Regime Detector
Styled as a financial broadsheet / newspaper front page.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
from regime_detector import SYMBOLS, run_analysis

# ---- Page config ----
st.set_page_config(
    page_title="The Regime Monitor",
    page_icon="◆",
    layout="wide",
)

# ---- Newspaper CSS ----
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Source+Serif+4:ital,wght@0,300;0,400;0,600;1,400&family=JetBrains+Mono:wght@400&display=swap');

/* Kill default Streamlit chrome */
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}

/* Base */
.stApp {
    background-color: #F5F0E8;
    color: #1A1A1D;
}

/* Override Streamlit's default text colors */
.stApp p, .stApp li, .stApp span, .stApp label {
    color: #2C2825;
}

/* Masthead */
.masthead {
    text-align: center;
    border-bottom: 4px double #1A1A1D;
    padding-bottom: 0.75rem;
    margin-bottom: 0.25rem;
}
.masthead h1 {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 3.2rem;
    font-weight: 900;
    color: #1A1A1D;
    letter-spacing: 0.04em;
    margin: 0;
    line-height: 1.1;
}
.masthead-sub {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.85rem;
    color: #5C5550;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 0.25rem;
}
.dateline {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.8rem;
    color: #8A8279;
    text-align: center;
    border-bottom: 1px solid #D4CFC6;
    border-top: 1px solid #D4CFC6;
    padding: 0.35rem 0;
    margin-bottom: 1.5rem;
}

/* Headline (regime status) */
.headline-wrapper {
    text-align: center;
    margin: 1.5rem 0 1rem;
}
.headline {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2rem;
    font-weight: 700;
    color: #1A1A1D;
    line-height: 1.2;
    margin: 0;
}
.headline-stress {
    color: #7A2020;
}
.subheadline {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1.05rem;
    font-weight: 300;
    color: #5C5550;
    font-style: italic;
    margin-top: 0.4rem;
}

/* Wire-style alert */
.wire-alert {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #7A2020;
    background: #F0E6E0;
    border-left: 3px solid #7A2020;
    padding: 0.6rem 1rem;
    margin: 1rem 0;
    letter-spacing: 0.02em;
}

/* Column stats */
.stat-row {
    display: flex;
    justify-content: center;
    gap: 3rem;
    border-top: 1px solid #D4CFC6;
    border-bottom: 1px solid #D4CFC6;
    padding: 0.8rem 0;
    margin: 1rem 0 1.5rem;
    flex-wrap: wrap;
}
.stat-item {
    text-align: center;
}
.stat-label {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #8A8279;
    margin-bottom: 0.15rem;
}
.stat-value {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #1A1A1D;
}

/* Section headers */
.section-rule {
    border: none;
    border-top: 1px solid #D4CFC6;
    margin: 2rem 0 0.5rem;
}
.section-head {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #1A1A1D;
    margin-bottom: 0.75rem;
}

/* Body text */
.body-text {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.92rem;
    color: #2C2825;
    line-height: 1.7;
    max-width: 640px;
}

/* Methodology */
.method-text {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.85rem;
    color: #5C5550;
    line-height: 1.7;
}

/* Footer */
.paper-footer {
    text-align: center;
    border-top: 4px double #1A1A1D;
    padding-top: 0.6rem;
    margin-top: 2.5rem;
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.75rem;
    color: #8A8279;
}
.paper-footer a {
    color: #5C5550;
    text-decoration: underline;
}

/* Fix Streamlit sidebar */
section[data-testid="stSidebar"] {
    background-color: #EDE8DF;
    border-right: 1px solid #D4CFC6;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] label {
    color: #2C2825;
    font-family: 'Source Serif 4', Georgia, serif;
}

/* Fix metric cards */
[data-testid="stMetricValue"] {
    display: none;
}
[data-testid="stMetricLabel"] {
    display: none;
}

/* Fix expander */
.streamlit-expanderHeader {
    font-family: 'Playfair Display', Georgia, serif;
    color: #1A1A1D;
}
</style>
""", unsafe_allow_html=True)

# ---- Sidebar ----
st.sidebar.markdown("## Edition settings")

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
with st.spinner("Typesetting..."):
    try:
        result = run_analysis(symbol, years, window)
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

# ---- Masthead ----
st.markdown("""
<div class="masthead">
    <h1>THE REGIME MONITOR</h1>
    <div class="masthead-sub">Energy Volatility Intelligence</div>
</div>
""", unsafe_allow_html=True)

# ---- Dateline ----
today = datetime.now().strftime("%A, %B %d, %Y")
st.markdown(f"""
<div class="dateline">
    {today} &nbsp;&bull;&nbsp; {symbol_name} front-month futures
    &nbsp;&bull;&nbsp; {window}-day rolling window
    &nbsp;&bull;&nbsp; {years}-year lookback
</div>
""", unsafe_allow_html=True)

# ---- Headline ----
stress_pct = result["current_stress_prob"] * 100
current_vol_pct = result["current_vol"] * 100
calm_vol = result["calm_mean_vol"] * 100
stress_vol = result["stress_mean_vol"] * 100

if result["current_regime"] == "STRESS":
    headline_class = "headline headline-stress"
    headline_text = f"{symbol_name} Markets Operating Under Stress Regime"
    subhead = f"Annualized volatility at {current_vol_pct:.1f}% with {stress_pct:.0f}% regime probability"
else:
    headline_class = "headline"
    headline_text = f"{symbol_name} Markets Holding in Calm Regime"
    subhead = f"Annualized volatility at {current_vol_pct:.1f}% with {100-stress_pct:.0f}% calm probability"

st.markdown(f"""
<div class="headline-wrapper">
    <h2 class="{headline_class}">{headline_text}</h2>
    <div class="subheadline">{subhead}</div>
</div>
""", unsafe_allow_html=True)

# ---- Alert (wire-service style) ----
if result["current_stress_prob"] >= alert_threshold:
    st.markdown(f"""
    <div class="wire-alert">
        REGIME ALERT &mdash; Stress probability at {stress_pct:.1f}%,
        exceeding the {alert_threshold*100:.0f}% threshold.
        Current annualized volatility: {current_vol_pct:.1f}%.
        Calm-regime average: {calm_vol:.1f}%. Stress-regime average: {stress_vol:.1f}%.
    </div>
    """, unsafe_allow_html=True)

# ---- Stats row ----
latest_price = result["prices"]["Close"].iloc[-1]
price_change = result["log_returns"].iloc[-1] * 100

st.markdown(f"""
<div class="stat-row">
    <div class="stat-item">
        <div class="stat-label">Last close</div>
        <div class="stat-value">${latest_price:.2f}</div>
    </div>
    <div class="stat-item">
        <div class="stat-label">Daily return</div>
        <div class="stat-value">{price_change:+.2f}%</div>
    </div>
    <div class="stat-item">
        <div class="stat-label">Annualized vol</div>
        <div class="stat-value">{current_vol_pct:.1f}%</div>
    </div>
    <div class="stat-item">
        <div class="stat-label">Stress probability</div>
        <div class="stat-value">{stress_pct:.0f}%</div>
    </div>
    <div class="stat-item">
        <div class="stat-label">Calm avg</div>
        <div class="stat-value">{calm_vol:.1f}%</div>
    </div>
    <div class="stat-item">
        <div class="stat-label">Stress avg</div>
        <div class="stat-value">{stress_vol:.1f}%</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---- Charts ----
st.markdown('<hr class="section-rule"><div class="section-head">Price History & Regime Overlay</div>', unsafe_allow_html=True)

fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.06,
    row_heights=[0.4, 0.3, 0.3],
    subplot_titles=[
        f"{symbol_name} (USD)",
        f"Rolling {window}-day annualized volatility",
        "Regime stress probability",
    ],
)

# Price
fig.add_trace(
    go.Scatter(
        x=result["prices"].index,
        y=result["prices"]["Close"],
        name="Price",
        line=dict(color="#2C2825", width=1.2),
    ),
    row=1, col=1,
)

# Stress shading
states = result["regime"]["states"]
stress_state = result["regime"]["stress_state"]
stress_mask = states == stress_state

if stress_mask.any():
    diff = stress_mask.astype(int).diff().fillna(0)
    starts = states.index[diff == 1].tolist()
    ends = states.index[diff == -1].tolist()
    if stress_mask.iloc[0]:
        starts.insert(0, states.index[0])
    if stress_mask.iloc[-1]:
        ends.append(states.index[-1])
    for s, e in zip(starts, ends):
        for row in [1, 2]:
            fig.add_vrect(
                x0=s, x1=e,
                fillcolor="rgba(122, 32, 32, 0.08)",
                layer="below",
                line_width=0,
                row=row, col=1,
            )

# Volatility
vol = result["volatility"].dropna()
fig.add_trace(
    go.Scatter(
        x=vol.index,
        y=vol.values * 100,
        name="Vol (%)",
        line=dict(color="#4A6741", width=1.5),
    ),
    row=2, col=1,
)

fig.add_hline(y=calm_vol, line_dash="dot", line_color="#4A6741",
              annotation_text=f"Calm: {calm_vol:.1f}%", row=2, col=1)
fig.add_hline(y=stress_vol, line_dash="dot", line_color="#7A2020",
              annotation_text=f"Stress: {stress_vol:.1f}%", row=2, col=1)

# Changepoints
for cp in result["changepoints"]:
    if cp in vol.index:
        fig.add_vline(x=cp, line_dash="dash", line_color="#8A8279",
                      line_width=0.8, row=2, col=1)

# Stress probability
stress_prob = result["regime"]["stress_prob"]
fig.add_trace(
    go.Scatter(
        x=stress_prob.index,
        y=stress_prob.values * 100,
        name="Stress prob (%)",
        fill="tozeroy",
        fillcolor="rgba(122, 32, 32, 0.12)",
        line=dict(color="#7A2020", width=1.5),
    ),
    row=3, col=1,
)

fig.add_hline(y=alert_threshold * 100, line_dash="dash", line_color="#8A8279",
              annotation_text=f"Alert: {alert_threshold*100:.0f}%", row=3, col=1)

# Chart styling — newspaper feel
fig.update_layout(
    height=750,
    showlegend=False,
    template="plotly_white",
    paper_bgcolor="#F5F0E8",
    plot_bgcolor="#F5F0E8",
    font=dict(family="Source Serif 4, Georgia, serif", color="#2C2825", size=11),
    margin=dict(l=50, r=20, t=30, b=30),
)

fig.update_xaxes(gridcolor="#E0DCD4", linecolor="#D4CFC6", tickfont=dict(size=10))
fig.update_yaxes(gridcolor="#E0DCD4", linecolor="#D4CFC6", tickfont=dict(size=10))

st.plotly_chart(fig, use_container_width=True)

# ---- Methodology ----
st.markdown('<hr class="section-rule"><div class="section-head">Methodology Notes</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="method-text">
    <strong>Volatility calculation.</strong> Daily log returns (ln P<sub>t</sub> / P<sub>t-1</sub>)
    are computed from closing prices. Rolling standard deviation over the configured window
    is annualized by &radic;252. This produces a continuously updated estimate of how much
    the market is moving relative to its own recent history.
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="method-text">
    <strong>Regime classification.</strong> A two-state Gaussian Hidden Markov Model is fit to the
    volatility series. The model learns two distributions (calm and stress), the transition
    probabilities between them, and the most likely state at each time step. The stress probability
    displayed is the model's posterior estimate that today belongs to the elevated-volatility regime.
    </div>
    """, unsafe_allow_html=True)

# ---- Footer ----
st.markdown("""
<div class="paper-footer">
    The Regime Monitor is a research tool, not financial advice.
    Built by <a href="https://gabyhernandez.dev">Gaby Hernandez</a>.
    Data from Yahoo Finance. Model recalibrates on each page load.
</div>
""", unsafe_allow_html=True)
