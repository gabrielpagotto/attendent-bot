from crewai import Agent, Task

from langchain.llms.openai import OpenAIChat
from config import config


class AppointmentAgent(Agent):

    def __init__(self):
        super().__init__(
            name="Agente de Agendamentos",
            role="Especialista em Agendamentos",
            goal="Realizar agendamentos de forma eficiente e precisa.",
            backstory="""Você é um especialista em agendamentos com vasta experiência em agendamentos.
            """,
            llm=OpenAIChat(
                model="gpt-4o-mini", temperature=0.5, api_key=config.openai_api_key
            ),
        )

    def run(self, context: str) -> str:
        return self.execute_task(
            Task(
                description="Agendar um atendimento para o cliente.",
                agent=self,
                expected_output="string",
            )
        )
