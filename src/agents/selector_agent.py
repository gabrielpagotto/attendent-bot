from typing import List
from crewai import Task

from langchain.llms.openai import OpenAIChat
from src.agents.base_agent import BaseAgent
from config import config


class SelectorAgent(BaseAgent):

    def __init__(self, history: List[dict]):
        super().__init__(
            name="Você deve selecionar o agente mais adequado para o cliente com base no histórico de conversa",
            role="Especialista em Seleção de Agentes",
            goal="Analisar o histórico de conversa e selecionar o agente mais adequado para o cliente",
            backstory=(
                "Histórico de conversa com o usuário:\n"
                f"{SelectorAgent.mount_history(history)}\n\n"
                "Agentes disponíveis:\n"
                "  CÓDIGO, NOME\n"
                "- first_contact_agent: As primeiras conversas com o cliente. Utilizado para conversar com o cliente até que você identifique qual agente deve ser utilizado\n"
                "- appointment_agent: Utilizar quando pelo histórico o cliente quer realizar um agendamento\n"
                "- sales_agent: Utilizar quando pelo histórico o cliente quer comprar algo\n"
                "- support_agent: Utilizar quando pelo histórico o cliente quer entrar em contato com o suporte\n"
                "- payment_agent: Utilizar quando pelo histórico o cliente quer realizar um pagamento\n\n"
                "Seu retorno deve ser somente a string bruta com o código do agente selecionado. NADA MAIS!\n"
            ),
            llm=OpenAIChat(
                model="gpt-4o-mini", temperature=0.5, api_key=config.openai_api_key
            ),
        )

    def run(self, context: str) -> str:
        return self.execute_task(
            Task(
                description="Selecionar para qual agente o cliente deve ser direcionado",
                agent=self,
                expected_output="string",
            )
        )
