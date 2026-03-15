from agent.memory_engine import load_memory, save_memory


def get_watchlist():

    print("[tools] get_watchlist called with no parameters")

    return load_memory("watchlist.json")


def add_to_watchlist(ticker):

    print(f"[tools] add_to_watchlist called with ticker={ticker}")

    watchlist = load_memory("watchlist.json")

    if "tickers" not in watchlist:
        watchlist["tickers"] = []

    if ticker not in watchlist["tickers"]:
        watchlist["tickers"].append(ticker)

    save_memory("watchlist.json", watchlist)

    return watchlist