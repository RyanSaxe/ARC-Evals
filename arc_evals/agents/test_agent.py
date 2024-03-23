import os
from pathlib import Path

from arc_evals.agents.base import Agent


class TestAgent(Agent):
    """An Agent that is allowed to cheat, so all metrics should be perfect"""

    def call(self, data):
        return [answer for answer in data["test"]]


EVAL_PATH = Path(__file__).parent.parent.parent / "evals"
DATA_PATH = Path(__file__).parent.parent.parent / "data/training"

if __name__ == "__main__":
    agent = TestAgent(DATA_PATH, EVAL_PATH, "cheater")
    for json_filename in os.listdir(DATA_PATH):
        agent(json_filename)
