from agent.memory_engine import load_memory, save_memory


def set_strategy(strategy):

    save_memory("strategy.json", strategy)

    return {"status": "strategy saved"}


def get_strategy():

    return load_memory("strategy.json")