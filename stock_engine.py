import yfinance as yf
import pandas as pd
import numpy as np

print("==== STOCK DECISION ENGINE ====\n")

ticker = input("Enter ticker (e.g., AMD): ").upper()
portfolio_size = float(input("Total portfolio size ($): "))
current_position_value = float(input("Current invested amount in this stock ($): "))
invested_amount = current_position_value

if invested_amount > 0:
    entry_price = float(input("Your average entry price: "))
else:
    entry_price = None

extra_cash = float(input("Extra cash available to deploy ($): "))
risk_percent = float(input("Max risk % per position (e.g., 2 for 2%): ")) / 100
portfolio_size = portfolio_size + extra_cash

print("\nFetching data...\n")

stock = yf.Ticker(ticker)
df_daily = stock.history(period="2y")
df_weekly = stock.history(period="2y", interval="1wk")

if df_daily.empty or df_weekly.empty:
    print("Error: No data fetched. Check ticker symbol.")
    exit()

def detect_swing_points(df, lookback=5):
    swing_highs = []
    swing_lows = []

    for i in range(lookback, len(df) - lookback):
        high = df["High"].iloc[i]
        low = df["Low"].iloc[i]

        if high == max(df["High"].iloc[i-lookback:i+lookback+1]):
            swing_highs.append(high)

        if low == min(df["Low"].iloc[i-lookback:i+lookback+1]):
            swing_lows.append(low)

    return swing_highs, swing_lows

current_price = df_daily["Close"].iloc[-1]

df_weekly["H-L"] = df_weekly["High"] - df_weekly["Low"]
df_weekly["H-PC"] = abs(df_weekly["High"] - df_weekly["Close"].shift(1))
df_weekly["L-PC"] = abs(df_weekly["Low"] - df_weekly["Close"].shift(1))
df_weekly["TR"] = df_weekly[["H-L", "H-PC", "L-PC"]].max(axis=1)
df_weekly["ATR_14"] = df_weekly["TR"].rolling(14).mean()
weekly_atr = df_weekly["ATR_14"].iloc[-1]

df_daily.index = pd.to_datetime(df_daily.index)

six_month_high = df_daily["High"].rolling(126).max().iloc[-1]
high_index = df_daily[df_daily["High"] == six_month_high].index[-1]
post_high_data = df_daily.loc[high_index:]
recent_low = post_high_data["Low"].min()
recent_high = six_month_high
diff = recent_high - recent_low

print(f"Recent Low (6M): ${round(recent_low,2)}")

swing_highs, swing_lows = detect_swing_points(df_daily)

# Safe swing fallback
if len(swing_highs) >= 5:
    recent_high = max(swing_highs[-5:])
else:
    recent_high = max(swing_highs)

if len(swing_lows) >= 5:
    recent_low = min(swing_lows[-5:])
else:
    recent_low = min(swing_lows)

diff = recent_high - recent_low

fib_levels = {
    "0.236": recent_high - 0.236 * diff,
    "0.382": recent_high - 0.382 * diff,
    "0.5": recent_high - 0.5 * diff,
    "0.618": recent_high - 0.618 * diff,
}

def detect_support_levels(df, lookback=3, tolerance=0.02):
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

        classified.append((zone["price"], strength, zone["touches"]))

    classified = sorted(classified, key=lambda x: x[0], reverse=True)
    return classified

supports = detect_support_levels(df_daily)

print("\n========== STRUCTURAL SUPPORT LEVELS ==========")
for price, strength, touches in supports[:5]:
    print(f"${round(price,2)}  |  {strength}  |  Touches: {touches}")

atr_stop_1_5 = current_price - (1.5 * weekly_atr)
atr_stop_2 = current_price - (2 * weekly_atr)

# SAFE POSITION CALCULATION
if entry_price is not None and current_position_value > 0:
    shares_owned = current_position_value / entry_price
    risk_per_share = entry_price - atr_stop_1_5
    total_risk = shares_owned * risk_per_share

    if portfolio_size > 0:
        portfolio_risk_percent = (total_risk / portfolio_size) * 100
    else:
        portfolio_risk_percent = 0
else:
    shares_owned = 0
    risk_per_share = 0
    total_risk = 0
    portfolio_risk_percent = 0

# SAFE NEW POSITION SIZING
if portfolio_size > 0:
    max_risk_dollars = portfolio_size * risk_percent
else:
    max_risk_dollars = 0

fresh_risk_per_share = current_price - atr_stop_1_5

if fresh_risk_per_share > 0:
    optimal_shares = max_risk_dollars / fresh_risk_per_share
else:
    optimal_shares = 0

print("========== LIVE DATA ==========")
print(f"Current Price: ${round(current_price,2)}")
print(f"Weekly ATR (14): ${round(weekly_atr,2)}")

print("\n========== STRUCTURE ==========")
print(f"Recent High (6M): ${round(recent_high,2)}")

print("\n========== FIB LEVELS ==========")
for k, v in fib_levels.items():
    print(f"Fib {k}: ${round(v,2)}")

print("\n========== STOPS ==========")
print(f"1.5x ATR Stop: ${round(atr_stop_1_5,2)}")
print(f"2x ATR Stop: ${round(atr_stop_2,2)}")

print("\n========== YOUR POSITION ==========")
if shares_owned > 0:
    print(f"Shares Owned: {round(shares_owned,2)}")
    print(f"Risk Per Share: ${round(risk_per_share,2)}")
    print(f"Total Risk: ${round(total_risk,2)}")
    print(f"Portfolio Risk: {round(portfolio_risk_percent,2)}%")
else:
    print("No current position.")

print("\n========== NEW POSITION SIZING ==========")
print(f"Max Allowed Risk ($): ${round(max_risk_dollars,2)}")
print(f"Optimal Shares if fresh entry: {round(optimal_shares,2)}")

print("\n========== CASH DEPLOYMENT CHECK ==========")
if extra_cash > 0:
    potential_shares = extra_cash / current_price
    print(f"You can buy approx {round(potential_shares,2)} more shares with extra cash.")
else:
    print("No extra cash available.")

print("\n===========================================")