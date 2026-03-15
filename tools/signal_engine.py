"""
Signal engine: swing points, support levels, and structure analysis.

- All structure calculations use WEEKLY bars only (interval="1wk").
- Swing high/low: local extremum over a window of (2*lookback+1) bars.
- "Recent" high/low used for Fib and range: max/min of last 5 swing highs/lows
  to stabilise indicator pivots on the weekly timeframe.
"""
import numpy as np
import yfinance as yf


def detect_swing_points(df, lookback=5):
    """
    Find swing highs and swing lows: bars whose High (Low) is the max (min)
    over [i-lookback, i+lookback]. Returns lists of (timestamp, price) so
    callers can use time order (e.g. most recent swing).
    """
    print(f"[tools] detect_swing_points called with lookback={lookback}")

    if df is None or len(df) == 0:
        return [], []

    swing_highs = []  # (timestamp, price)
    swing_lows = []

    for i in range(lookback, len(df) - lookback):
        ts = df.index[i]
        high = float(df["High"].iloc[i])
        low = float(df["Low"].iloc[i])

        if high == max(df["High"].iloc[i - lookback : i + lookback + 1]):
            swing_highs.append((ts, high))
        if low == min(df["Low"].iloc[i - lookback : i + lookback + 1]):
            swing_lows.append((ts, low))

    return swing_highs, swing_lows


def detect_support_levels(df, lookback=3, tolerance=0.02):
    """
    Build support zones from swing lows: cluster nearby lows (within tolerance),
    score by touches and volume. Zones are over the full series; for more
    stable levels on daily data, consider using weekly bars in analyze_structure.
    """
    print(
        f"[tools] detect_support_levels called with "
        f"lookback={lookback}, tolerance={tolerance}"
    )

    if df is None or len(df) == 0 or "Volume" not in df.columns:
        return []

    df = df.copy()
    df["Volume_MA20"] = df["Volume"].rolling(20).mean()
    swing_lows = []

    for i in range(lookback, len(df) - lookback):
        low = df["Low"].iloc[i]
        if low == min(df["Low"].iloc[i-lookback:i+lookback+1]):
            swing_lows.append((df.index[i], low, df["Volume"].iloc[i]))

    zones = []

    for date, price, volume in swing_lows:
        added = False

        for zone in zones:
            if abs(price - zone["price"]) / zone["price"] < tolerance:
                zone["touches"] += 1
                zone["volumes"].append(volume)
                zone["dates"].append(date)
                zone["price"] = np.mean([zone["price"], price])
                added = True
                break

        if not added:
            zones.append({
                "price": price,
                "touches": 1,
                "volumes": [volume],
                "dates": [date]
            })

    classified = []

    for zone in zones:
        avg_volume = np.mean(zone["volumes"])
        recent_touch = max(zone["dates"])
        recency_score = (df.index.max() - recent_touch).days

        score = 0

        if zone["touches"] >= 3:
            score += 2
        elif zone["touches"] == 2:
            score += 1

        if avg_volume > df["Volume_MA20"].mean():
            score += 1

        if recency_score < 60:
            score += 1

        if score >= 4:
            strength = "STRONG"
        elif score >= 2:
            strength = "MEDIUM"
        else:
            strength = "WEAK"

        classified.append({
            "price": float(zone["price"]),
            "strength": strength,
            "touches": zone["touches"]
        })

    classified = sorted(classified, key=lambda x: x["price"], reverse=True)

    return classified


def analyze_structure(ticker, interval="1wk"):
    """
    Analyze price structure (swing range, Fib levels, supports) for a ticker.
    Uses weekly bars only (interval="1wk"); interval argument is kept for API
    compatibility but is ignored — structure is always computed on weekly data.
    """
    interval = "1wk"  # enforce weekly only
    print(f"[tools] analyze_structure called with ticker={ticker}, interval={interval}")

    df = yf.Ticker(ticker).history(period="2y", interval=interval)

    if df is None or df.empty:
        print(f"[tools] analyze_structure: no price data for {ticker}, skipping")
        return {"ticker": ticker, "error": "no_data"}

    if not {"High", "Low", "Volume"}.issubset(df.columns):
        print(f"[tools] analyze_structure: missing columns for {ticker}, skipping")
        return {"ticker": ticker, "error": "bad_schema"}

    swing_highs, swing_lows = detect_swing_points(df)

    if not swing_highs or not swing_lows:
        print(f"[tools] analyze_structure: insufficient swing points for {ticker}")
        return {"ticker": ticker, "error": "insufficient_history"}

    # Fib retracement: use the most recent swing high, and the swing low that
    # occurred *before* that high (the prior low we retrace from). So we do
    # not use a low whose date is after the high.
    pivot_high_ts, pivot_high_price = swing_highs[-1]

    lows_before_high = [(ts, p) for ts, p in swing_lows if ts < pivot_high_ts]
    if lows_before_high:
        pivot_low_ts, pivot_low_price = min(lows_before_high, key=lambda x: x[1])
    else:
        pivot_low_ts, pivot_low_price = swing_lows[-1]

    recent_high = max(pivot_high_price, pivot_low_price)
    recent_low = min(pivot_high_price, pivot_low_price)

    # Print pivot information: Fib is drawn from high down to prior low (low date before high date).
    print(
        f"[tools] analyze_structure pivots for {ticker}: "
        f"high={pivot_high_price:.2f} on {pivot_high_ts}, "
        f"low={pivot_low_price:.2f} on {pivot_low_ts}"
    )

    diff = recent_high - recent_low

    if diff == 0:
        print(f"[tools] analyze_structure: zero range for {ticker}")
        return {"ticker": ticker, "error": "flat_price"}

    fib_levels = {
        "0.236": recent_high - 0.236 * diff,
        "0.382": recent_high - 0.382 * diff,
        "0.5": recent_high - 0.5 * diff,
        "0.618": recent_high - 0.618 * diff,
    }

    supports = detect_support_levels(df)

    return {
        "ticker": ticker,
        "interval": interval,
        "recent_high": float(recent_high),
        "recent_low": float(recent_low),
        "fib_levels": fib_levels,
        "supports": supports[:5],
    }