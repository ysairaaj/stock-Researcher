import pandas as pd
from tools.market_data_engine import get_market_data


def backtest_strategy(
    ticker,
    strategy="trend_pullback",
    initial_capital=10000
):
    print(
        f"[tools] backtest_strategy called with "
        f"ticker={ticker}, strategy={strategy}, initial_capital={initial_capital}"
    )
    
    data = get_market_data(ticker)

    df = pd.DataFrame(data)

    df["ma50"] = df["close"].rolling(50).mean()
    df["ma20"] = df["close"].rolling(20).mean()

    trades = []

    capital = initial_capital
    position = None

    for i in range(50, len(df)):

        price = df["close"].iloc[i]

        # -------- Trend Pullback --------

        if strategy == "trend_pullback":

            if price > df["ma50"].iloc[i] and price < df["ma20"].iloc[i]:

                entry = price
                stop = entry * 0.97
                target = entry * 1.06

                position = (entry, stop, target)

        # -------- Breakout --------

        if strategy == "breakout":

            prev_high = df["high"].iloc[i-20:i].max()

            if price > prev_high:

                entry = price
                stop = entry * 0.95
                target = entry * 1.10

                position = (entry, stop, target)

        # -------- Mean Reversion --------

        if strategy == "mean_reversion":

            prev_low = df["low"].iloc[i-10:i].min()

            if price < prev_low:

                entry = price
                stop = entry * 0.97
                target = entry * 1.04

                position = (entry, stop, target)

        # -------- Trade management --------

        if position:

            entry, stop, target = position

            if price <= stop:

                capital *= 0.97
                trades.append("loss")
                position = None

            elif price >= target:

                capital *= 1.06
                trades.append("win")
                position = None

    wins = trades.count("win")
    losses = trades.count("loss")

    total = wins + losses

    win_rate = wins / total if total > 0 else 0

    return {
        "ticker": ticker,
        "strategy": strategy,
        "trades": total,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "final_capital": capital,
        "return_pct": (capital - initial_capital) / initial_capital
    }