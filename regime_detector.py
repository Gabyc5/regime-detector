"""
regime_detector.py
Core engine for energy market regime change detection.
Computes rolling log-return volatility and classifies market state
using a two-state Hidden Markov Model (calm vs. stress).
"""

import numpy as np
import pandas as pd
import yfinance as yf
from hmmlearn.hmm import GaussianHMM
from datetime import datetime, timedelta


# ---- Data fetching ----

SYMBOLS = {
    "WTI Crude": "CL=F",
    "Brent Crude": "BZ=F",
    "Natural Gas": "NG=F",
    "RBOB Gasoline": "RB=F",
    "Heating Oil": "HO=F",
}


def fetch_prices(symbol: str = "CL=F", years: int = 5) -> pd.DataFrame:
    """Fetch daily close prices from Yahoo Finance."""
    end = datetime.now()
    start = end - timedelta(days=years * 365)
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start, end=end, auto_adjust=True)
    if df.empty:
        raise ValueError(f"No data returned for {symbol}")
    return df[["Close"]].dropna()


# ---- Volatility computation ----

def compute_log_returns(prices: pd.DataFrame) -> pd.Series:
    """Compute daily log returns from close prices."""
    return np.log(prices["Close"] / prices["Close"].shift(1)).dropna()


def rolling_volatility(log_returns: pd.Series, window: int = 21) -> pd.Series:
    """
    Compute rolling annualized volatility.
    Default window = 21 trading days (1 month).
    Annualized by sqrt(252).
    """
    return log_returns.rolling(window=window).std() * np.sqrt(252)


# ---- Regime detection (HMM) ----

def fit_regime_model(vol_series: pd.Series, n_states: int = 2) -> dict:
    """
    Fit a two-state Gaussian HMM to the volatility series.
    Returns the model, predicted states, and state probabilities.
    """
    clean = vol_series.dropna().values.reshape(-1, 1)
    idx = vol_series.dropna().index

    model = GaussianHMM(
        n_components=n_states,
        covariance_type="full",
        n_iter=200,
        random_state=42,
    )
    model.fit(clean)

    states = model.predict(clean)
    probs = model.predict_proba(clean)

    # Identify which state is "stress" (higher mean vol)
    means = model.means_.flatten()
    stress_state = int(np.argmax(means))
    calm_state = 1 - stress_state

    return {
        "model": model,
        "states": pd.Series(states, index=idx, name="regime"),
        "stress_prob": pd.Series(probs[:, stress_state], index=idx, name="stress_probability"),
        "calm_prob": pd.Series(probs[:, calm_state], index=idx, name="calm_probability"),
        "stress_state": stress_state,
        "calm_state": calm_state,
        "stress_mean_vol": means[stress_state],
        "calm_mean_vol": means[calm_state],
    }


# ---- Changepoint detection (simpler alternative) ----

def detect_changepoints(vol_series: pd.Series, penalty: int = 10) -> list:
    """
    Detect structural breaks in volatility using the ruptures library.
    Returns a list of breakpoint indices.
    """
    try:
        import ruptures as rpt
    except ImportError:
        return []

    clean = vol_series.dropna().values
    algo = rpt.Pelt(model="rbf").fit(clean)
    breakpoints = algo.predict(pen=penalty)
    # Convert indices back to dates
    idx = vol_series.dropna().index
    dates = [idx[bp - 1] for bp in breakpoints if bp < len(idx)]
    return dates


# ---- Full pipeline ----

def run_analysis(symbol: str = "CL=F", years: int = 5, window: int = 21) -> dict:
    """
    Run the full regime detection pipeline.
    Returns all computed data for dashboard display.
    """
    prices = fetch_prices(symbol, years)
    log_ret = compute_log_returns(prices)
    vol = rolling_volatility(log_ret, window)
    regime = fit_regime_model(vol)
    changepoints = detect_changepoints(vol)

    # Current regime assessment
    latest_stress_prob = regime["stress_prob"].iloc[-1]
    latest_vol = vol.iloc[-1]
    current_regime = "STRESS" if latest_stress_prob > 0.5 else "CALM"

    return {
        "prices": prices,
        "log_returns": log_ret,
        "volatility": vol,
        "regime": regime,
        "changepoints": changepoints,
        "current_regime": current_regime,
        "current_stress_prob": latest_stress_prob,
        "current_vol": latest_vol,
        "calm_mean_vol": regime["calm_mean_vol"],
        "stress_mean_vol": regime["stress_mean_vol"],
    }
