from agent.model_manager import ask_with_fallback


def ask_llm(prompt, model=None):

    return ask_with_fallback(prompt, model_override=model)