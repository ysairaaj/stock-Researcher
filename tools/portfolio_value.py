from tools.portfolio_memory import get_portfolio


def get_portfolio_value(default_value=10000):

    print(f"[tools] get_portfolio_value called with default_value={default_value}")

    portfolio = get_portfolio()

    if not portfolio:
        return {"portfolio_value": default_value}

    total = 0

    for ticker, position in portfolio.items():

        shares = position["shares"]
        entry = position["entry_price"]

        total += shares * entry

    return {"portfolio_value": total}