import json
import os

MEMORY_DIR = "memory"
CONVERSATION_FILE = "conversation.json"


def load_memory(file):

    path = os.path.join(MEMORY_DIR, file)

    if not os.path.exists(path):
        return {}

    with open(path, "r") as f:
        return json.load(f)


def save_memory(file, data):

    os.makedirs(MEMORY_DIR, exist_ok=True)

    path = os.path.join(MEMORY_DIR, file)

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# --------------------------
# Conversation Memory
# --------------------------

def load_conversation():

    path = os.path.join(MEMORY_DIR, CONVERSATION_FILE)

    if not os.path.exists(path):
        return []

    with open(path, "r") as f:
        return json.load(f)


def save_conversation(history):

    os.makedirs(MEMORY_DIR, exist_ok=True)

    path = os.path.join(MEMORY_DIR, CONVERSATION_FILE)

    with open(path, "w") as f:
        json.dump(history, f, indent=2)


def add_message(role, content):

    history = load_conversation()

    history.append({
        "role": role,
        "content": content
    })

    # Rolling memory management
    if len(history) > 30:
        history = history[10:]   # remove oldest 10 messages

    save_conversation(history)

    return history