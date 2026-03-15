from agent.memory_engine import load_memory, save_memory


def get_portfolio():

    print("[tools] get_portfolio called with no parameters")

    return load_memory("portfolio.json")


def add_position(ticker, entry_price, shares):

    print(
        f"[tools] add_position called with "
        f"ticker={ticker}, entry_price={entry_price}, shares={shares}"
    )

    portfolio = load_memory("portfolio.json")

    portfolio[ticker] = {
        "entry_price": entry_price,
        "shares": shares
    }

    save_memory("portfolio.json", portfolio)

    return {"status": "position added", "portfolio": portfolio}


def remove_position(ticker):

    print(f"[tools] remove_position called with ticker={ticker}")

    portfolio = load_memory("portfolio.json")

    if ticker in portfolio:
        del portfolio[ticker]

    save_memory("portfolio.json", portfolio)

    return {"status": "position removed"}