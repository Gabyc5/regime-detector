"""
app.py
The Regime Monitor — Energy Volatility Intelligence
Styled after vintage financial almanacks and broadsheets.
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
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---- CSS ----
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;0,8..60,600;1,8..60,300;1,8..60,400&family=JetBrains+Mono:wght@400&display=swap');

/* Kill Streamlit chrome */
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}
.block-container {padding-top: 0.5rem !important; max-width: 780px;}

/* Aged paper background */
.stApp {
    background: #E8E0D0;
    background-image: url("https://www.transparenttextures.com/patterns/natural-paper.png");
    color: #2C2420;
}

/* Layered paper card */
.paper-stack {
    position: relative;
    background: #F2ECE0;
    background-image: url("https://www.transparenttextures.com/patterns/natural-paper.png");
    border: 1px solid #C8BFA8;
    padding: 2.5rem 2.5rem 2rem;
    margin: 0 0 0.5rem;
    box-shadow:
        3px 3px 0 #E0D8C8,
        6px 6px 0 #D4CCB8,
        9px 9px 0 #C8C0AC;
}

/* Masthead */
.masthead {
    text-align: center;
    padding-bottom: 0.6rem;
    margin-bottom: 0.1rem;
}
.masthead-locale {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.65rem;
    color: #8A8070;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}
.masthead h1 {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2.6rem;
    font-weight: 900;
    color: #1A1815;
    letter-spacing: 0.05em;
    margin: 0;
    line-height: 1.05;
}
.masthead-sub {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.72rem;
    color: #6B6355;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    margin-top: 0.15rem;
}
.masthead-rule {
    border: none;
    border-top: 3px double #1A1815;
    margin: 0.5rem 0 0.15rem;
}
.masthead-rule-thin {
    border: none;
    border-top: 1px solid #1A1815;
    margin: 0.15rem 0 0;
}

/* Dateline */
.dateline {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.72rem;
    color: #8A8070;
    text-align: center;
    padding: 0.35rem 0;
    border-bottom: 1px solid #C8BFA8;
    margin-bottom: 1rem;
}

/* Edition number */
.edition-no {
    text-align: center;
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 0.7rem;
    font-style: italic;
    color: #8A8070;
    margin-bottom: 0.8rem;
}

/* Regime badge */
.regime-badge {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    padding: 0.25rem 0.9rem;
    border-radius: 1px;
    margin-bottom: 0.5rem;
}
.badge-stress { background: #5C1010; color: #F2ECE0; }
.badge-calm { background: #2E4A2E; color: #F2ECE0; }

/* Headline */
.headline-wrapper { text-align: center; margin: 0.5rem 0 0.6rem; }
.headline {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.85rem;
    font-weight: 900;
    color: #1A1815;
    line-height: 1.15;
    margin: 0;
}
.headline-stress { color: #5C1010; }
.subheadline {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.92rem;
    font-weight: 300;
    color: #6B6355;
    font-style: italic;
    margin-top: 0.3rem;
}

/* Wire alert */
.wire-alert {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #5C1010;
    background: #E8DDD0;
    border-left: 3px solid #5C1010;
    padding: 0.5rem 0.9rem;
    margin: 0.6rem 0;
    line-height: 1.6;
}

/* Stats row */
.stat-row {
    display: flex;
    justify-content: space-between;
    border-top: 1px solid #C8BFA8;
    border-bottom: 1px solid #C8BFA8;
    padding: 0.6rem 0;
    margin: 0.6rem 0 1rem;
    flex-wrap: wrap;
    gap: 0.3rem;
}
.stat-item { text-align: center; flex: 1; min-width: 80px; }
.stat-label {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.58rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #8A8070;
    margin-bottom: 0.1rem;
}
.stat-value {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #1A1815;
}

/* Section ornaments */
.section-orn {
    text-align: center;
    color: #B0A890;
    font-size: 0.9rem;
    margin: 1.5rem 0 0.3rem;
    letter-spacing: 0.5em;
}
.section-head {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1rem;
    font-weight: 700;
    color: #1A1815;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid #C8BFA8;
    padding-bottom: 0.3rem;
}

/* Body text */
.body-serif {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.88rem;
    color: #3A3530;
    line-height: 1.75;
    text-align: justify;
    hyphens: auto;
}
.body-serif strong {
    font-weight: 600;
    color: #1A1815;
}

/* Reading / narrative */
.reading-box {
    background: #EAE3D4;
    border: 1px solid #C8BFA8;
    padding: 1.2rem 1.4rem;
    margin: 0.8rem 0;
}
.reading-label {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 0.7rem;
    font-style: italic;
    color: #8A8070;
    margin-bottom: 0.4rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
}
.reading-text {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.92rem;
    font-style: italic;
    color: #3A3530;
    line-height: 1.7;
}

/* Ledger table */
.ledger-table {
    width: 100%;
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.8rem;
    border-collapse: collapse;
    color: #3A3530;
}
.ledger-table th {
    font-family: 'Playfair Display', Georgia, serif;
    font-weight: 700;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #8A8070;
    text-align: left;
    padding: 0.35rem 0.5rem;
    border-bottom: 2px solid #C8BFA8;
}
.ledger-table td {
    padding: 0.3rem 0.5rem;
    border-bottom: 1px solid #D8D0C0;
}
.ledger-stress { color: #5C1010; font-weight: 600; }
.ledger-calm { color: #2E4A2E; font-weight: 600; }

/* Method columns */
.method-text {
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.8rem;
    color: #6B6355;
    line-height: 1.7;
    text-align: justify;
}

/* Footer */
.paper-footer {
    text-align: center;
    border-top: 3px double #1A1815;
    padding-top: 0.5rem;
    margin-top: 1.5rem;
    font-family: 'Source Serif 4', Georgia, serif;
    font-size: 0.68rem;
    color: #8A8070;
}
.paper-footer a { color: #5C1010; text-decoration: underline; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #E8E0D0;
    background-image: url("https://www.transparenttextures.com/patterns/natural-paper.png");
    border-right: 1px solid #C8BFA8;
}
[data-testid="stSidebarContent"] { padding-top: 0.5rem !important; }
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] label {
    color: #2C2420 !important;
    font-family: 'Source Serif 4', Georgia, serif;
}

/* Green sliders */
div[data-baseweb="slider"] div[role="slider"] {
    background: #2E4A2E !important;
    border-color: #2E4A2E !important;
}
div[data-baseweb="slider"] div[data-testid="stTickBar"] > div {
    background: #2E4A2E !important;
}

/* Hide Streamlit metric elements */
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] { display: none; }

/* Override Streamlit text */
.stApp p, .stApp li, .stApp span, .stApp label { color: #2C2420; }
</style>
""", unsafe_allow_html=True)

# ---- Sidebar ----
st.sidebar.markdown("## Edition Settings")
st.sidebar.markdown(
    "<span style='font-size:0.75rem;color:#8A8070;font-style:italic;'>"
    "Adjust parameters below. Close this panel with the X above; "
    "reopen with the arrow at top-left.</span>",
    unsafe_allow_html=True,
)
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

# ---- Compute edition number (days since project start) ----
project_start = datetime(2026, 4, 25)
edition_no = (datetime.now() - project_start).days + 1

# ---- Derived values ----
stress_pct = result["current_stress_prob"] * 100
current_vol_pct = result["current_vol"] * 100
calm_vol = result["calm_mean_vol"] * 100
stress_vol = result["stress_mean_vol"] * 100
latest_price = result["prices"]["Close"].iloc[-1]
price_change = result["log_returns"].iloc[-1] * 100

# ---- START PAPER STACK ----
st.markdown('<div class="paper-stack">', unsafe_allow_html=True)

# Masthead
today = datetime.now().strftime("%A, %B %d, %Y")
st.markdown(f"""
<div class="masthead">
    <div class="masthead-locale">Houston, Texas &bull; Established 2026</div>
    <h1>THE REGIME MONITOR</h1>
    <div class="masthead-sub">Energy Volatility Intelligence</div>
    <hr class="masthead-rule">
    <hr class="masthead-rule-thin">
</div>
<div class="dateline">
    {today} &nbsp;&bull;&nbsp; {symbol_name} front-month futures
    &nbsp;&bull;&nbsp; {window}-day window
    &nbsp;&bull;&nbsp; {years}-year lookback
</div>
<div class="edition-no">No. {edition_no}</div>
""", unsafe_allow_html=True)

# Headline
if result["current_regime"] == "STRESS":
    headline_class = "headline headline-stress"
    badge_class = "regime-badge badge-stress"
    badge_text = "STRESS REGIME"
    headline_text = f"{symbol_name} Markets Under Stress"
    subhead = f"Volatility at {current_vol_pct:.1f}% annualized, {stress_pct:.0f}% stress probability"
else:
    headline_class = "headline"
    badge_class = "regime-badge badge-calm"
    badge_text = "CALM REGIME"
    headline_text = f"{symbol_name} Markets Holding Steady"
    subhead = f"Volatility at {current_vol_pct:.1f}% annualized, {100-stress_pct:.0f}% calm probability"

st.markdown(f"""
<div class="headline-wrapper">
    <div class="{badge_class}">{badge_text}</div>
    <h2 class="{headline_class}">{headline_text}</h2>
    <div class="subheadline">{subhead}</div>
</div>
""", unsafe_allow_html=True)

# Alert
if result["current_stress_prob"] >= alert_threshold:
    st.markdown(f"""
    <div class="wire-alert">
        REGIME ALERT &mdash; Stress probability {stress_pct:.1f}%, above {alert_threshold*100:.0f}% threshold.
        Vol: {current_vol_pct:.1f}%. Calm avg: {calm_vol:.1f}%. Stress avg: {stress_vol:.1f}%.
    </div>
    """, unsafe_allow_html=True)

# Stats
st.markdown(f"""
<div class="stat-row">
    <div class="stat-item"><div class="stat-label">Last close</div><div class="stat-value">${latest_price:.2f}</div></div>
    <div class="stat-item"><div class="stat-label">Daily return</div><div class="stat-value">{price_change:+.2f}%</div></div>
    <div class="stat-item"><div class="stat-label">Ann. vol</div><div class="stat-value">{current_vol_pct:.1f}%</div></div>
    <div class="stat-item"><div class="stat-label">Stress prob.</div><div class="stat-value">{stress_pct:.0f}%</div></div>
    <div class="stat-item"><div class="stat-label">Calm avg</div><div class="stat-value">{calm_vol:.1f}%</div></div>
    <div class="stat-item"><div class="stat-label">Stress avg</div><div class="stat-value">{stress_vol:.1f}%</div></div>
</div>
""", unsafe_allow_html=True)

# ---- Today's Reading ----
st.markdown('<div class="section-orn">&#9830; &#9830; &#9830;</div>', unsafe_allow_html=True)

# Generate narrative
vol_ratio = current_vol_pct / calm_vol if calm_vol > 0 else 1
if result["current_regime"] == "STRESS":
    if stress_pct > 90:
        narrative = (
            f"The model places {symbol_name} firmly in a stress regime with "
            f"{stress_pct:.0f}% confidence. Current volatility ({current_vol_pct:.1f}%) "
            f"is running {vol_ratio:.1f}x the calm-regime average. Risk parameters "
            f"calibrated on the last six months of calm data are likely understating "
            f"true exposure. VaR and margin calculations should be reviewed against "
            f"stress-regime assumptions."
        )
    else:
        narrative = (
            f"{symbol_name} is showing elevated stress signals ({stress_pct:.0f}% probability). "
            f"Volatility at {current_vol_pct:.1f}% sits between the calm average ({calm_vol:.1f}%) "
            f"and stress average ({stress_vol:.1f}%). This is the ambiguous zone where "
            f"regime transitions tend to happen. Worth monitoring closely over the next "
            f"few sessions."
        )
else:
    if stress_pct < 10:
        narrative = (
            f"{symbol_name} markets are firmly in a calm regime ({100-stress_pct:.0f}% confidence). "
            f"Volatility at {current_vol_pct:.1f}% is close to the calm-period average "
            f"of {calm_vol:.1f}%. Standard risk parameters are appropriate. No regime "
            f"transition signals detected."
        )
    else:
        narrative = (
            f"{symbol_name} is operating in a calm regime but with a non-trivial stress "
            f"reading ({stress_pct:.0f}%). Volatility at {current_vol_pct:.1f}% remains "
            f"near the calm average ({calm_vol:.1f}%), but the model is picking up early "
            f"signals that could precede a transition. Not actionable yet, but worth watching."
        )

st.markdown(f"""
<div class="reading-box">
    <div class="reading-label">Today's reading</div>
    <div class="reading-text">{narrative}</div>
</div>
""", unsafe_allow_html=True)

# ---- Charts ----
st.markdown('<div class="section-orn">&#9830; &#9830; &#9830;</div>', unsafe_allow_html=True)
st.markdown('<div class="section-head">Price, Volatility &amp; Regime History</div>', unsafe_allow_html=True)

fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.06,
    row_heights=[0.4, 0.3, 0.3],
    subplot_titles=[f"{symbol_name} (USD)", f"{window}-day annualized vol", "Stress probability"],
)

fig.add_trace(go.Scatter(
    x=result["prices"].index, y=result["prices"]["Close"],
    name="Price", line=dict(color="#2C2420", width=1.1),
), row=1, col=1)

# Stress shading
states = result["regime"]["states"]
stress_state = result["regime"]["stress_state"]
stress_mask = states == stress_state
if stress_mask.any():
    diff = stress_mask.astype(int).diff().fillna(0)
    starts = states.index[diff == 1].tolist()
    ends = states.index[diff == -1].tolist()
    if stress_mask.iloc[0]: starts.insert(0, states.index[0])
    if stress_mask.iloc[-1]: ends.append(states.index[-1])
    for s, e in zip(starts, ends):
        for row in [1, 2]:
            fig.add_vrect(x0=s, x1=e, fillcolor="rgba(92,16,16,0.06)",
                          layer="below", line_width=0, row=row, col=1)

vol = result["volatility"].dropna()
fig.add_trace(go.Scatter(
    x=vol.index, y=vol.values * 100, name="Vol",
    line=dict(color="#2E4A2E", width=1.4),
), row=2, col=1)

fig.add_hline(y=calm_vol, line_dash="dot", line_color="#2E4A2E",
              annotation_text=f"Calm: {calm_vol:.1f}%", row=2, col=1)
fig.add_hline(y=stress_vol, line_dash="dot", line_color="#5C1010",
              annotation_text=f"Stress: {stress_vol:.1f}%", row=2, col=1)

for cp in result["changepoints"]:
    if cp in vol.index:
        fig.add_vline(x=cp, line_dash="dash", line_color="#B0A890",
                      line_width=0.7, row=2, col=1)

stress_prob = result["regime"]["stress_prob"]
fig.add_trace(go.Scatter(
    x=stress_prob.index, y=stress_prob.values * 100, name="Stress",
    fill="tozeroy", fillcolor="rgba(92,16,16,0.08)",
    line=dict(color="#5C1010", width=1.4),
), row=3, col=1)
fig.add_hline(y=alert_threshold * 100, line_dash="dash", line_color="#B0A890",
              annotation_text=f"Alert: {alert_threshold*100:.0f}%", row=3, col=1)

fig.update_layout(
    height=680, showlegend=False, template="plotly_white",
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#F2ECE0",
    font=dict(family="Source Serif 4, Georgia, serif", color="#2C2420", size=10),
    margin=dict(l=45, r=15, t=25, b=25),
)
fig.update_xaxes(gridcolor="#DDD6C6", linecolor="#C8BFA8", tickfont=dict(size=9))
fig.update_yaxes(gridcolor="#DDD6C6", linecolor="#C8BFA8", tickfont=dict(size=9))

st.plotly_chart(fig, use_container_width=True)

# ---- Regime Transition Ledger ----
st.markdown('<div class="section-orn">&#9830; &#9830; &#9830;</div>', unsafe_allow_html=True)
st.markdown('<div class="section-head">Regime Transition Ledger</div>', unsafe_allow_html=True)

# Find transitions
state_series = result["regime"]["states"]
transitions = state_series.diff().fillna(0)
change_idx = transitions[transitions != 0].index

if len(change_idx) > 0:
    rows_html = ""
    for idx in change_idx[-12:]:  # Last 12 transitions
        new_state = state_series.loc[idx]
        sp = result["regime"]["stress_prob"].loc[idx] * 100
        v = result["volatility"].loc[idx] * 100 if idx in result["volatility"].index else 0
        if new_state == stress_state:
            state_label = '<span class="ledger-stress">STRESS</span>'
        else:
            state_label = '<span class="ledger-calm">CALM</span>'
        date_str = idx.strftime("%b %d, %Y")
        rows_html += f"<tr><td>{date_str}</td><td>{state_label}</td><td>{v:.1f}%</td><td>{sp:.0f}%</td></tr>"

    st.markdown(f"""
    <table class="ledger-table">
        <tr><th>Date</th><th>Regime</th><th>Vol</th><th>Stress Prob.</th></tr>
        {rows_html}
    </table>
    """, unsafe_allow_html=True)
else:
    st.markdown('<div class="body-serif">No regime transitions detected in the selected period.</div>',
                unsafe_allow_html=True)

# ---- Historical Context ----
st.markdown('<div class="section-orn">&#9830; &#9830; &#9830;</div>', unsafe_allow_html=True)
st.markdown('<div class="section-head">Notable Regime Shifts in Energy Markets</div>', unsafe_allow_html=True)

st.markdown("""
<div class="body-serif" style="column-count:2; column-gap:1.5rem; column-rule: 1px solid #C8BFA8;">
<strong>Feb–Mar 2022.</strong> Russia invades Ukraine. WTI annualized vol jumps from ~31% to ~79%
in days. Brent spikes above $130. European natural gas prices hit all-time highs.
Risk models calibrated on 2021 data were immediately obsolete.
<br><br>
<strong>Mar–Apr 2020.</strong> COVID lockdowns collapse demand. WTI futures briefly go negative
($-37.63 on April 20). Vol explodes past 200% annualized. OPEC+ emergency cuts fail to
stabilize prices for weeks.
<br><br>
<strong>Nov 2014.</strong> OPEC refuses to cut production despite US shale boom. WTI drops from $80 to
$45 in two months. A regime shift that most models only flagged after the damage was done.
<br><br>
<strong>Jul–Oct 2008.</strong> WTI falls from $147 to $34 during the financial crisis. The
largest single-direction move in crude oil history. Volatility regimes that had been
calm for years blew out in weeks.
</div>
""", unsafe_allow_html=True)

# ---- Methodology ----
st.markdown('<div class="section-orn">&#9830; &#9830; &#9830;</div>', unsafe_allow_html=True)
st.markdown('<div class="section-head">Methodology Notes</div>', unsafe_allow_html=True)

st.markdown("""
<div class="method-text" style="column-count:2; column-gap:1.5rem; column-rule: 1px solid #C8BFA8;">
<strong>Volatility.</strong> Daily log returns are computed as ln(P_t / P_{t-1}).
Rolling standard deviation over the configured window is annualized by
multiplying by √252. This produces a continuously updated estimate of
realized volatility relative to recent history.
<br><br>
<strong>Regime classification.</strong> A two-state Gaussian Hidden Markov Model
(hmmlearn) is fit to the annualized volatility series. The model learns two
emission distributions (calm and stress), a 2×2 transition matrix, and computes
the posterior state probability at each time step via the forward-backward algorithm.
The "stress probability" displayed is the model's posterior estimate that today's
observation belongs to the elevated-volatility state.
<br><br>
<strong>Changepoint detection.</strong> The PELT algorithm (ruptures library) independently
identifies structural breaks in the volatility series by minimizing a penalized
cost function. Breakpoints mark dates where the statistical properties of volatility
change, regardless of what the HMM says. When both methods agree, confidence is higher.
<br><br>
<strong>Limitations.</strong> The model is backward-looking. It detects regime shifts
after they begin, not before. The two-state assumption is a simplification; real
markets may have more than two regimes. Data is end-of-day, not intraday. This is
a research and monitoring tool, not a trading signal.
</div>
""", unsafe_allow_html=True)

# ---- Editor's Note ----
st.markdown('<div class="section-orn">&#9830; &#9830; &#9830;</div>', unsafe_allow_html=True)
st.markdown('<div class="section-head">Editor\'s Note</div>', unsafe_allow_html=True)

st.markdown("""
<div class="body-serif">
This tool exists because risk models fail quietly. They don't throw errors
when the market changes underneath them. They just keep running the same math
on data that no longer describes the world. I built this after spending weeks
studying how a major energy trading firm lost hundreds of millions when their
risk parameters couldn't keep up with a regime shift they didn't detect in time.
<br><br>
The Regime Monitor doesn't predict what will happen. It tells you which
statistical world you're in right now, so you can decide whether your numbers
still mean what you think they mean.
<br><br>
<em style="color:#8A8070;">— G. Hernandez, Houston, 2026</em>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="paper-footer">
    The Regime Monitor is a research instrument, not financial advice. &bull;
    Built by <a href="https://gabyhernandez.dev">Gaby Hernandez</a> &bull;
    Data via Yahoo Finance &bull; Model recalibrates on each load
</div>
""", unsafe_allow_html=True)

# Close paper stack
st.markdown('</div>', unsafe_allow_html=True)
