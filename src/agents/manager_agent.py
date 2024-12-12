from crewai import Agent, Crew, Process, Task
from langchain_community.chat_models import ChatOpenAI
from config import config

from src import utils
from src import tools
from src.services import Services
from src.database import Client


class ScreeningAgent:

    def __init__(self, services: Services, client: Client) -> None:
        self.services = services
        self.client = client
        self.conversations = self.services.get_client_conversation(client)

        company = self.services.get_company()
        products = self.services.get_products()

        client_informations = utils.create_client_informations(self.client)
        history_informations = utils.create_history_informations(self.conversations)
        company_informations = utils.create_company_informations(company)

        save_client_names_tool = tools.SaveClientNamesTool(services=self.services, client=self.client)
        close_current_conversation_tool = tools.CloseCurrentConversation(services=self.services, client=self.client)

        self.screening_agent = Agent(
            name="Agende de atendimento inicial",
            role="Triagem e conhecedor do cliente",
            goal="Garantir o primeiro contato com o cliente de forma simpática e agradável e encontrar o objetivo do cliente.",
            tools=[save_client_names_tool, close_current_conversation_tool],
            backstory=f"""
                Você é um profissional responsável por realizar a triagem do cliente incial de forma simples e agradável.
                Antes de realizar qualquer ação você deve descobrir nome e sobrenome do cliente e salva-lo na base de dados, porém isso deve ser feito somente quando for descoberto ou o nome mudar.
                Você deve chamar gentilmente o cliente pelo nome
                Você deve sempre realizar o que o cliente te pedir

                Sempre que o cliente adicionar informações inválidas, advita-o para que ele coloque corretamente.
                Você deve continuar a conversa fluentemente com base no histórico!

                Você pode fornecer os seguintes serviços Informações da empresa e Realizar pedidos via delivery (Utilizando order_agent)!
                Tenha certeza do nome do cliente antes de realizar qualquer tipo de serviço!

                Caso a conversa seja relacionada a qualquer questão de produtos ou pedidos olhando como base o histórico ou como base no que o usuário está pedindo, você deve retornar a palavra "order_agent" apensas em sua resposta, essa palavra servirá para redirecionar para o setor de produtos/pedidos.

                {client_informations}
                {history_informations}
                {company_informations}
            """,
        )

        order = services.get_order_by_client(client)

        products_informations = utils.create_products_list(products)
        order_informations = utils.create_order_informations(order)

        create_order_tool = tools.CreateOrderTool(services=services, client=client)
        add_product_in_order_tool = tools.AddProductInOrderTool(services=services, client=client)
        remove_product_in_order_tool = tools.RemoveProductInOrderTool(services=services, client=client)
        change_product_quantity_in_order_tool = tools.ChangeProductQuantityInOrderTool(
            services=services, client=client
        )

        self.order_agent = Agent(
            role="Controlador de pedidos de produtos",
            goal="Garantir que o cliente possa visualizar os produtos disponíveis, criar pedidos adicionando produtos, listar pedidos já realizados e lançar novos pedidos",
            tools=[
                create_order_tool,
                add_product_in_order_tool,
                remove_product_in_order_tool,
                change_product_quantity_in_order_tool,
                close_current_conversation_tool,
            ],
            backstory=f"""
                Você é um profissional responsável por garantir que o cliente possa controlar seus pedidos por completo como visualizar, cancelar, realizar novos pedidos.
                Se o ID da ordem não existir você deve perguntar o cliente se ele deseja realizar um novo, pedido, se ele quiser deve ser criado uma nova ordem.
                Você nunca deve mostrar os IDS e codes dos produtos para os clientes, somente nome e preço.
                Você deve controlar de maneira profissional quando o cliente deseja visualizar, incluir, cancelar ou alterar quantidade de produtos no pedido.
                Para utilizar as ferramentas você deve utilizar os IDs informados como order_id, product_id e order_product_id.
                Para a seleção na lista de produtos você sempre levar em consideração o product_id.
                Você sempre deve encontrar o product_id referente pelo nome, caso esteja mal escrito e esteja causando dúvidas em qual produto selecionar você deve pedir para o cliente ser mais claro na escolha dos produtos.
                Se o cliente não informar a quantidade do pedido você deve pergunta-lo.
                Somente poderá ser editado orders que estão com status em "open".
                Antes de finalizar o pedido, é preciso que o cliente garanta que todos os itens estão em conformidade com o que ele escolheu, portanto ele precisa confirmar antes.

                Você deve continuar a conversa fluentemente com base no histórico!

                {client_informations}
                {history_informations}
                {products_informations}
                {order_informations}
            """,
        )

    def _execute_screening_agent(self, task: Task) -> str:
        task.agent = self.screening_agent

        crew = Crew(
            agents=[self.screening_agent],
            tasks=[task],
            process=Process.sequential,
            llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.5, api_key=config.openai_api_key),
        )
        crew.kickoff()
        return task.output.raw, "screening_agent"

    def _execute_order_agent(self, task: Task) -> tuple[str, str]:
        task.agent = self.order_agent
        crew = Crew(
            agents=[self.screening_agent],
            tasks=[task],
            process=Process.sequential,
            llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.5, api_key=config.openai_api_key),
        )
        crew.kickoff()
        return task.output.raw, "order_agent"

    def run(self, task: Task) -> tuple[str, str]:
        agents = ["screening_agent", "order_agent"]
        using_agent = self.conversations[-1].agent if len(self.conversations) > 0 else agents[0]
        while using_agent is not None and using_agent in agents:
            output, agent = {
                agents[0]: self._execute_screening_agent(task),
                agents[1]: self._execute_order_agent(task),
            }[using_agent]

            if output not in agents:
                return output, agent
            using_agent = output
