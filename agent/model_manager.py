import requests
import subprocess
import time


OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL_PRIORITY = [
    "qwen2.5:32b",
    "deepseek-r1:32b",
    "qwen2.5:32b",
    "llama3:8b"
]


def is_server_running():
    try:
        requests.get("http://localhost:11434")
        return True
    except:
        return False


def start_server():
    print("Starting Ollama server...")
    subprocess.Popen(["ollama", "serve"])
    time.sleep(5)


def ensure_server():
    if not is_server_running():
        start_server()


def ask_model(model, prompt):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]


def ask_with_fallback(prompt, model_override=None):

    ensure_server()

    models = MODEL_PRIORITY

    if model_override:
        models = [model_override] + models

    for model in models:

        try:
            print(f"Trying model: {model}")

            response = ask_model(model, prompt)

            return response

        except Exception as e:

            print(f"Model failed: {model}")
            continue

    raise Exception("All models failed")