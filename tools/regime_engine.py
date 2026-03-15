import pandas as pd
import numpy as np
import yfinance as yf


def detect_market_regime(symbol="SPY"):

    print(f"[tools] detect_market_regime called with symbol={symbol}")

    # Use full price history directly from yfinance; get_market_data only
    # returns scalars and is not suitable for regime detection.
    df = yf.Ticker(symbol).history(period="2y")

    if df is None or df.empty or "Close" not in df.columns:
        print(f"[tools] detect_market_regime: no data for {symbol}, defaulting")
        return {
            "symbol": symbol,
            "trend": "sideways",
            "volatility": "normal_volatility",
            "volatility_value": 0.0,
        }

    df = df.copy()
    df["ma50"] = df["Close"].rolling(50).mean()
    df["ma200"] = df["Close"].rolling(200).mean()

    df["returns"] = df["Close"].pct_change()

    # Require at least 200 bars so MAs are meaningful
    if len(df) < 200:
        print(f"[tools] detect_market_regime: insufficient history for {symbol}")
        return {
            "symbol": symbol,
            "trend": "sideways",
            "volatility": "normal_volatility",
            "volatility_value": 0.0,
        }

    volatility = df["returns"].rolling(20).std().iloc[-1]

    price = df["Close"].iloc[-1]
    ma50 = df["ma50"].iloc[-1]
    ma200 = df["ma200"].iloc[-1]

    # ----- Trend detection -----

    if price > ma50 > ma200:
        trend = "bull"
    elif price < ma50 < ma200:
        trend = "bear"
    else:
        trend = "sideways"

    # ----- Volatility detection -----

    if volatility > 0.03:
        volatility_regime = "high_volatility"
    else:
        volatility_regime = "normal_volatility"

    return {
        "symbol": symbol,
        "trend": trend,
        "volatility": volatility_regime,
        "volatility_value": float(volatility),
    }