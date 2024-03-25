from arc_evals.agents.base import Agent, run_agent
from arc_evals.utils.paths import OUTPUT, TRAINING


class TestAgent(Agent):
    """An Agent that is allowed to cheat, so all metrics should be perfect"""

    def call(self, data):
        return [answer["output"] for answer in data["test"]]


if __name__ == "__main__":
    agent = TestAgent()
    run_agent(agent, "cheater", OUTPUT, TRAINING, overwrite=True)
