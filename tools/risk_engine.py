def calculate_position_risk(entry_price, current_price, atr, shares_owned, portfolio_size, risk_percent):

    print(
        f"[tools] calculate_position_risk called with "
        f"entry_price={entry_price}, current_price={current_price}, atr={atr}, "
        f"shares_owned={shares_owned}, portfolio_size={portfolio_size}, "
        f"risk_percent={risk_percent}"
    )

    atr_stop = current_price - (1.5 * atr)

    risk_per_share = entry_price - atr_stop
    total_risk = shares_owned * risk_per_share

    portfolio_risk_percent = (total_risk / portfolio_size) * 100 if portfolio_size > 0 else 0

    max_risk_dollars = portfolio_size * risk_percent

    fresh_risk_per_share = current_price - atr_stop

    optimal_shares = max_risk_dollars / fresh_risk_per_share if fresh_risk_per_share > 0 else 0

    return {
        "risk_per_share": float(risk_per_share),
        "total_risk": float(total_risk),
        "portfolio_risk_percent": float(portfolio_risk_percent),
        "max_risk_dollars": float(max_risk_dollars),
        "optimal_shares": float(optimal_shares),
        "atr_stop": float(atr_stop)
    }