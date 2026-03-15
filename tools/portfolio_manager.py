from tools.market_data_engine import get_market_data
from tools.risk_engine import calculate_position_risk


def evaluate_position(ticker, entry_price, shares_owned, portfolio_size, risk_percent):

    print(
        f"[tools] evaluate_position called with "
        f"ticker={ticker}, entry_price={entry_price}, "
        f"shares_owned={shares_owned}, portfolio_size={portfolio_size}, "
        f"risk_percent={risk_percent}"
    )

    market = get_market_data(ticker)

    if "error" in market:
        return market

    risk = calculate_position_risk(
        entry_price,
        market["current_price"],
        market["weekly_atr"],
        shares_owned,
        portfolio_size,
        risk_percent
    )

    return {
        "ticker": ticker,
        "market": market,
        "risk": risk
    }