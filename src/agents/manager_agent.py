from typing import Any
from crewai import Agent, Crew, Process, Task
from langchain_community.chat_models import ChatOpenAI
from config import config

from src import utils
from src import tools
from src.services import Services
from src.database import Client



class TaskProcessor:

    def __init__(self, task: Task, services: Services, client: Client) -> None:
        self.task = task
        self.services = services
        self.client = client

    # @tool
    # def save_client_names_tool(self, first_name: str, last_name: str):
    #     """Ferramenta que deverá chamada assim que descobrir o nome e sobrenome do cliente, caso nome e sobrenome do cliente já sejam conhecidos, esta ferramente não deve ser utilizada."""

    #     print("Salvando...")
    #     print({"nome": first_name, "sobrenome": last_name})

    def process_task(self) -> str:

        company = self.services.get_company()

        client_informations = utils.create_client_informations(self.client)
        history_listing = utils.create_history_listing(self.client.conversations)
        company_listing = utils.create_company_listing(company)

        appointment_agent = Agent(
            name="Agente de Agendamento",
            role="Atendente experiente em agendamentos.",
            goal="Realizar agendamentos de forma eficiente e garantir a satisfação do cliente.",
            allow_delegation=False,
            verbose=True,
            backstory=f"""
            Você é um atendente experiente em agendamentos.

            {history_listing}

            Dados obrigatórios para agendamento, pergunte um por vez:
            - Nome
            - Email
            - Telefone
            - Data
            - Horário

            Horários de atendimento:
            - Segunda à sexta: 08:00 às 18:00
            - Sábado: 08:00 às 12:00

            Ao ser solicitado um agendamento, você deve verificar as informações obrigatórias e agendar o compromisso.
            """,
        )

        sales_agent = Agent(
            name="Agente de Vendas",
            role="Realizar uma venda ao cliente.",
            goal="Realizar uma venda ao cliente.",
            allow_delegation=False,
            backstory=f"""
            Existem os seguintes produtos:
            - Produto Coca Cola: R$ 100,00
            - Produto Pepsi: R$ 200,00
            - Produto Fanta: R$ 300,00
            """,
        )

        manager_agent = Agent(
            name="Agente principal",
            role="Gerencie a equipe de forma eficiente e garanta a conclusão de tarefas de alta qualidade",
            goal="Identificar a intenção do cliente e direcionar para o agente mais adequado.",
            allow_delegation=True,
            backstory=f"""
            Você é o primeiro contato com o cliente experiente, habilidoso em atendimento ao cliente e orientar para o agente mais adequado.

            O que se espera de você:
            - Você deve conversar com o cliente para identificar qual a intenção dele.
            - Você deve tentar identificar qual a intenção do cliente, quando não estiver claro para você, você deve perguntar para o cliente.
            - Você deve saudar o cliente utilizando o nome da empresa.
            - Ao identificar o que o cliente deseja, você deve direcionar para o agente mais adequado.
            - Para iniciar a conversa, você deve perguntar o que o cliente deseja.

            - Caso o cliente deseje realizar uma agendamento, você deve utilizar o atendente de agendamentos.

            Informações da empresa:
            - Nome: Armored Group
            - Endereço: Rua dos Bobos, 0 - São Paulo, SP
            - Telefone: (11) 99999-9999
            """,
        )

        save_client_names_tool = tools.SaveClientNamesTool(services=self.services, client=self.client)

        first_contact_agent = Agent(
            name="Agende de atendimento inicial",
            role="Triagem e conhecedor do cliente",
            goal="Garantir o primeiro contato com o cliente de forma simpática e agradável e encontrar o objetivo do cliente.",
            tools=[save_client_names_tool],
            backstory=f"""
                Você é um profissional responsável por realizar a triagem do cliente incial de forma simples e agradável.
                Antes de realizar qualquer ação você deve descobrir nome e sobrenome do cliente e salva-lo na base de dados, porém isso deve ser feito somente quando for descoberto ou o nome mudar.
                Você deve chamar gentilmente o cliente pelo nome
                Você deve sempre realizar o que o cliente te pedir

                Sempre que o cliente adicionar informações inválidas, advita-o para que ele coloque corretamente.
                Você deve continuar a conversa fluentemente com base no histórico!

                {client_informations}
                {history_listing}
                {company_listing}
            """,
        )

        self.task.agent = first_contact_agent

        crew = Crew(
            agents=[first_contact_agent],
            tasks=[self.task],
            process=Process.sequential,
            llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.5, api_key=config.openai_api_key),
        )
        crew.kickoff()

        return self.task.output.raw
