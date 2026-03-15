def calculate_position_size(
    portfolio_size,
    entry_price,
    stop_loss,
    risk_percent=0.02
):

    print(
        f"[tools] calculate_position_size called with "
        f"portfolio_size={portfolio_size}, entry_price={entry_price}, "
        f"stop_loss={stop_loss}, risk_percent={risk_percent}"
    )

    risk_amount = portfolio_size * risk_percent

    risk_per_share = abs(entry_price - stop_loss)

    if risk_per_share == 0:
        return {"error": "invalid stop loss"}

    shares = risk_amount / risk_per_share

    position_value = shares * entry_price

    return {
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "risk_percent": risk_percent,
        "risk_amount": risk_amount,
        "shares": int(shares),
        "position_value": position_value
    }