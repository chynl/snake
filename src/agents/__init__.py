from src.agents.base import Agent
from src.mode import Mode


def init_agent(mode: Mode) -> Agent | None:
    if mode == Mode.GRAPH:
        from src.agents.graph import GraphAgent

        return GraphAgent()

    if mode == Mode.RL:
        from src.agents.rl import RLAgent

        return RLAgent()

    return None
