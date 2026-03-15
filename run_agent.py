import argparse
from agent.agent_controller import run_agent

parser = argparse.ArgumentParser()

parser.add_argument(
    "--model",
    type=str,
    help="Override model"
)

args = parser.parse_args()

print("==== LOCAL TRADING AI ====\n")

while True:

    query = input("Ask: ")

    result = run_agent(query, model=args.model)

    print("\nAI:\n")
    print(result)
    print("\n-----------------\n")