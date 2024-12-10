from typing import List
from crewai import Crew, Agent, Task

from langchain.llms.openai import OpenAIChat
from src.agents.base_agent import BaseAgent
from config import config


def __get_first_contact_agent(history: List[dict]) -> Agent:
    return Agent(
        name="Agente de Triagem",
        role="Especialista em Atendimento Inicial",
        goal="Realizar a triagem inicial, responder perguntas e direcionar o cliente para o setor mais adequado, proporcionando uma experiência eficiente e acolhedora.",
        backstory="""
            Você é um especialista em atendimento inicial, e seu papel é ajudar os clientes com suas primeiras interações. 
            Abaixo está o histórico de conversa entre você e o cliente:
            {history}

            Serviços disponíveis:
            - Agendamentos: Marcar ou consultar compromissos.
            - Vendas: Assistência com produtos e compras.
            - Suporte: Resolver problemas técnicos ou dúvidas gerais.
            - Pagamentos: Auxiliar com cobranças, faturas ou problemas relacionados.

            Instruções específicas:
            1. **Primeiro contato:** Se for o primeiro contato com o cliente, dê as boas-vindas de forma simples e direta e não forneça os serviços no primeiro contato, somente pergunte qual o serviço ele deseja, caso não existe liste para ele os existentes.
            2. **Contatos subsequentes:** Pergunte ao cliente qual serviço ele deseja utilizar hoje, de formas simples e diretas, baseado no histórico.
            3. **Pergunta sobre serviços disponíveis:** Liste os serviços de forma simples e enumeradas.
            4. **Procura por serviço específico:** Esclareça os serviços disponíveis e solicite que o cliente detalhe melhor o que procura para que você possa ajudá-lo da melhor forma.

            Caso agendamento seja escolhido você deve responder: agendamento escolhido.
            Caso venda seja escolhido você deve responder: venda escolhida.
            Caso suporte seja escolhido você deve responder: suporte escolhido.
            Caso pagamento seja escolhido você deve responder: pagamento escolhido.
            """.format(
            history=BaseAgent.mount_history(history)
        ),
        llm=OpenAIChat(
            model="gpt-4o-mini", temperature=0.5, api_key=config.openai_api_key
        ),
    )


def __get_first_contact_task(input: str, agent: Agent) -> Task:
    return Task(
        description=input,
        expected_output="Resposta curta e direta que direciona o cliente para o próximo passo.",
        agent=agent,
    )


def execute_first_contact_task(input: str, history: List[dict]) -> str:
    agent = __get_first_contact_agent(history)
    task = __get_first_contact_task(input, agent)
    crew = Crew(agents=[agent], tasks=[task])
    crew.kickoff()
    return task.output.raw
