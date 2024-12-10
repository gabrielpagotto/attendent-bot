from crewai import Agent, Task

from langchain.llms.openai import OpenAIChat
from config import config


class SalesAgent(Agent):

    def __init__(self):
        super().__init__(
            name="Agente de Vendas",
            role="Especialista em Vendas",
            goal="Realizar vendas de forma eficiente e precisa.",
            backstory="""Você é um especialista em vendas com vasta experiência em vendas.
            """,
            llm=OpenAIChat(
                model="gpt-4o-mini", temperature=0.5, api_key=config.openai_api_key
            ),
        )

    def run(self, context: str) -> str:
        return self.execute_task(
            Task(
                description="Realizar uma venda para o cliente.",
                agent=self,
                expected_output="string",
            )
        )
