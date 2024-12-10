from typing import List
from crewai import Agent


class BaseAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, context: str):
        pass

    @staticmethod
    def mount_history(history: List[dict]):
        return "\n".join(
            [f"Usuário: {item['message']}\nVocê: {item['output']}" for item in history]
        )
