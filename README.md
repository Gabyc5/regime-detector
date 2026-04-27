# Energy Market Regime Change Detector

A real-time dashboard that monitors energy commodity markets for volatility regime shifts using statistical changepoint detection and Hidden Markov Models.

## What it does

Energy markets can operate in two fundamentally different states: **calm** (normal volatility, mean-reverting) and **stress** (elevated volatility, fat-tailed returns). Risk models calibrated on calm-regime data will dramatically underestimate exposure when the market transitions to stress. This tool detects those transitions.

The detector:
- Fetches daily price data for energy futures (WTI, Brent, Natural Gas, Gasoline, Heating Oil)
- Computes rolling log-return volatility with configurable windows
- Fits a two-state Gaussian Hidden Markov Model to classify calm vs. stress regimes
- Runs PELT changepoint detection to identify structural breaks
- Displays a live dashboard with regime probability gauge and alert system

## Why this matters

In February 2022, WTI crude oil's annualized volatility jumped from ~31% to ~79% in a matter of days. Any VaR model calibrated on the prior 6 months of data was using the wrong distribution. This detector would have flagged that regime shift within the first trading sessions.

The same logic applies to any energy market dislocation: supply disruptions, geopolitical events, policy shocks. The tool doesn't predict *what* will happen — it tells you *which statistical world you're living in* so risk parameters can be adjusted accordingly.

## Setup

```bash
# Clone
git clone https://github.com/Gabyc5/regime-detector.git
cd regime-detector

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

No API keys needed. Data comes from Yahoo Finance via yfinance.

## Project structure

```
regime-detector/
├── app.py                 # Streamlit dashboard
├── regime_detector.py     # Core detection engine
├── requirements.txt       # Python dependencies
├── .gitignore
└── README.md
```

## How the math works

**Log returns:** $$ln(P_t / P_{t-1})$$ - the continuously compounded return. Log returns are additive over time and approximately normally distributed, which is why they're used instead of simple percentage returns.

**Rolling volatility:** Standard deviation of log returns over a rolling window (default: 21 trading days = 1 month), annualized by multiplying by √252.

**Hidden Markov Model:** A two-state Gaussian HMM treats the volatility series as emissions from a hidden process that switches between two states. The model learns:
- The mean and variance of each state (calm vol ~ 25-35%, stress vol ~ 60-100%)
- The transition probabilities between states
- The most likely state sequence (Viterbi path)
- The probability of being in each state at every time step

**Changepoint detection (PELT):** The Pruned Exact Linear Time algorithm finds the optimal segmentation of the volatility series by minimizing a penalized cost function. Each segment has constant statistical properties; boundaries between segments are structural breaks.

## Configuration

All parameters are adjustable in the sidebar:
- **Commodity:** WTI, Brent, Natural Gas, RBOB Gasoline, Heating Oil
- **History:** 1-10 years of data
- **Rolling window:** 5-63 trading days (1 week to 3 months)
- **Alert threshold:** Stress probability level that triggers a warning (default: 70%)

## Tech stack

Python, Streamlit, Plotly, yfinance, hmmlearn, ruptures, pandas, NumPy

By: Gaby Hernandez:  [gabyhernandez.dev](https://gabyhernandez.dev)      [LinkedIn](https://www.linkedin.com/in/gaby-hernandez-gomez/)
