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
    initial_sidebar_state="expanded",
)

# ---- Newspaper CSS ----
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Source+Serif+4:ital,wght@0,300;0,400;0,600;1,400&family=JetBrains+Mono:wght@400&display=swap');

/* Kill default Streamlit chrome and top padding */
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}

.block-container {
    padding-top: 1rem !important;
    max-width: 1100px;
}

/* Paper texture background using CSS noise */
.stApp {
    background-color: #F5F0E8;
    background-image:
        url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
    color: #1A1A1D;
}

/* Subtle paper grain overlay */
.stApp::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background:
        radial-gradient(ellipse at 20% 50%, rgba(139,119,101,0.04) 0%, transparent 70%),
        radial-gradient(ellipse at 80% 20%, rgba(139,119,101,0.03) 0%, transparent 60%),
        radial-gradient(ellipse at 50% 80%, rgba(139,119,101,0.02) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

/* Override Streamlit text colors */
.stApp p, .stApp li, .stApp span, .stApp label {
    color: #2C2825;
}

/* Green sliders */
.stSlider > div > div > div > div {
    background-color: #4A6741 !important;
}
.stSlider > div > div > div:nth-child(1) > div {
    background: #4A6741 !important;
}
.stSlider [data-testid="stThumbValue"] {
    color: #2C2825 !important;
}
input[type="range"]::-webkit-slider-thumb {
    background: #4A6741 !important;
}
div[data-baseweb="slider"] div[role="slider"] {
    background: #4A6741 !important;
    border-color: #4A6741 !important;
}
div[data-baseweb="slider"] div[data-testid="stTickBar"] > div {
    background: #4A6741 !important;
}

/* Selectbox styling */
div[data-baseweb="select"] {
    border-color: #D4CFC6 !important;
}

/* Masthead */
.masthead {
    text-align: center;
    border-bottom: 4px double #1A1A1D;
    padding-bottom: 0.6rem;
    margin-bottom: 0.15rem;
}
.masthead h1 {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2.8rem;
    font-weight: 900;
    color: #1A1A1D;
    letter-spacing: 0.06em;
    margin: 0;
    line-height: 1.1;
}
.masthead-sub {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.8rem;
    color: #5C5550;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-top: 0.2rem;
}
.dateline {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.75rem;
    color: #8A8279;
    text-align: center;
    border-bottom: 1px solid #D4CFC6;
    border-top: 1px solid #D4CFC6;
    padding: 0.3rem 0;
    margin-bottom: 1rem;
}

/* Headline (regime status) - MUCH stronger emphasis */
.headline-wrapper {
    text-align: center;
    margin: 1rem 0 0.75rem;
    padding: 1rem 0;
}
.headline {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2.2rem;
    font-weight: 900;
    color: #1A1A1D;
    line-height: 1.15;
    margin: 0;
}
.headline-stress {
    color: #6B1515;
    text-shadow: 0 1px 0 rgba(107,21,21,0.1);
}

/* Regime badge */
.regime-badge {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 400;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding: 0.3rem 1rem;
    border-radius: 2px;
    margin-bottom: 0.6rem;
}
.badge-stress {
    background: #6B1515;
    color: #F5F0E8;
}
.badge-calm {
    background: #3A5C3A;
    color: #F5F0E8;
}

.subheadline {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 1rem;
    font-weight: 300;
    color: #5C5550;
    font-style: italic;
    margin-top: 0.4rem;
}

/* Wire-style alert */
.wire-alert {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #6B1515;
    background: #EDE3DC;
    border-left: 3px solid #6B1515;
    padding: 0.55rem 1rem;
    margin: 0.75rem 0;
    letter-spacing: 0.02em;
    line-height: 1.6;
}

/* Column stats */
.stat-row {
    display: flex;
    justify-content: center;
    gap: 2.5rem;
    border-top: 1px solid #D4CFC6;
    border-bottom: 1px solid #D4CFC6;
    padding: 0.7rem 0;
    margin: 0.75rem 0 1.25rem;
    flex-wrap: wrap;
}
.stat-item {
    text-align: center;
}
.stat-label {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #8A8279;
    margin-bottom: 0.1rem;
}
.stat-value {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #1A1A1D;
}

/* Section headers */
.section-rule {
    border: none;
    border-top: 1px solid #D4CFC6;
    margin: 1.5rem 0 0.4rem;
}
.section-head {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #1A1A1D;
    margin-bottom: 0.6rem;
}

/* Methodology text */
.method-text {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.82rem;
    color: #5C5550;
    line-height: 1.7;
}

/* Footer */
.paper-footer {
    text-align: center;
    border-top: 4px double #1A1A1D;
    padding-top: 0.5rem;
    margin-top: 2rem;
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.72rem;
    color: #8A8279;
}
.paper-footer a {
    color: #5C5550;
    text-decoration: underline;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #EDE8DF;
    background-image:
        url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
    border-right: 1px solid #D4CFC6;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] label {
    color: #2C2825 !important;
    font-family: 'Source Serif 4', Georgia, serif;
}

/* Hide default metric cards (we use custom HTML) */
[data-testid="stMetricValue"] { display: none; }
[data-testid="stMetricLabel"] { display: none; }

/* Expander */
.streamlit-expanderHeader {
    font-family: 'Playfair Display', Georgia, serif !important;
    color: #1A1A1D !important;
}
</style>
""", unsafe_allow_html=True)

# ---- Sidebar ----
st.sidebar.markdown("## Edition settings")
st.sidebar.markdown("*Adjust parameters below. Close this panel with the X above, reopen with the arrow at top-left.*")

symbol_name = st.sidebar.selectbox("Commodity", list(SYMBOLS.keys()), index=0)
symbol = SYMBOLS[symbol_name]
years = st.sidebar.slider("History (years)", 1, 10, 5)
window = st.sidebar.slider("Rolling window (trading days)", 5, 63, 21)
alert_threshold = st.sidebar.slider("Stress alert threshold", 0.5, 0.95, 0.7, 0.05)

# ---- Run analysis ----
with st.spinner("Typesetting today's edition..."):
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
    badge_class = "regime-badge badge-stress"
    badge_text = "STRESS REGIME"
    headline_text = f"{symbol_name} Markets Operating Under Stress"
    subhead = f"Annualized volatility at {current_vol_pct:.1f}% with {stress_pct:.0f}% stress probability"
else:
    headline_class = "headline"
    badge_class = "regime-badge badge-calm"
    badge_text = "CALM REGIME"
    headline_text = f"{symbol_name} Markets Holding Steady"
    subhead = f"Annualized volatility at {current_vol_pct:.1f}% with {100-stress_pct:.0f}% calm probability"

st.markdown(f"""
<div class="headline-wrapper">
    <div class="{badge_class}">{badge_text}</div>
    <h2 class="{headline_class}">{headline_text}</h2>
    <div class="subheadline">{subhead}</div>
</div>
""", unsafe_allow_html=True)

# ---- Alert ----
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
                fillcolor="rgba(107, 21, 21, 0.07)",
                layer="below",
                line_width=0,
                row=row, col=1,
            )

# Volatility
vol = result["volatility"].dropna()
fig.add_trace(
    go.Scatter(
        x=vol.index, y=vol.values * 100,
        name="Vol (%)",
        line=dict(color="#4A6741", width=1.5),
    ),
    row=2, col=1,
)

fig.add_hline(y=calm_vol, line_dash="dot", line_color="#4A6741",
              annotation_text=f"Calm: {calm_vol:.1f}%", row=2, col=1)
fig.add_hline(y=stress_vol, line_dash="dot", line_color="#6B1515",
              annotation_text=f"Stress: {stress_vol:.1f}%", row=2, col=1)

for cp in result["changepoints"]:
    if cp in vol.index:
        fig.add_vline(x=cp, line_dash="dash", line_color="#8A8279",
                      line_width=0.8, row=2, col=1)

# Stress probability
stress_prob = result["regime"]["stress_prob"]
fig.add_trace(
    go.Scatter(
        x=stress_prob.index, y=stress_prob.values * 100,
        name="Stress prob (%)",
        fill="tozeroy",
        fillcolor="rgba(107, 21, 21, 0.1)",
        line=dict(color="#6B1515", width=1.5),
    ),
    row=3, col=1,
)

fig.add_hline(y=alert_threshold * 100, line_dash="dash", line_color="#8A8279",
              annotation_text=f"Alert: {alert_threshold*100:.0f}%", row=3, col=1)

fig.update_layout(
    height=720,
    showlegend=False,
    template="plotly_white",
    paper_bgcolor="rgba(245,240,232,0)",
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
    is the model's posterior estimate that today belongs to the elevated-volatility regime.
    </div>
    """, unsafe_allow_html=True)

# ---- Footer ----
st.markdown("""
<div class="paper-footer">
    The Regime Monitor is a research tool, not financial advice.
    Built by <a href="https://gabyhernandez.dev">Gaby Hernandez</a>.
    Data via Yahoo Finance. Model recalibrates on each page load.
</div>
""", unsafe_allow_html=True)
