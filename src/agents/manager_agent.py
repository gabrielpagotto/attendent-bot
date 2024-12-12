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

        self.start_order_tool = tools.StartOrder()
        save_client_names_tool = tools.SaveClientNamesTool(services=self.services, client=self.client)
        close_current_conversation_tool = tools.CloseCurrentConversation(services=self.services, client=self.client)

        self.screening_agent = Agent(
            name="Agente de triagem",
            role="Realizar a triagem, conhecer o cliente, responder perguntas e redirecionar para outros serviços",
            goal="Realizar a triagem do cliente de forma adqueda e adiquirir informações, responder perguntas e redirecionar para os serviços mais adequados",
            tools=[self.start_order_tool, save_client_names_tool, close_current_conversation_tool],
            backstory=f"""

                Você é um profissional para realizar o primeiro contato com o cliente e seu dever é realizar a triagem de forma adequada, adiquirindo informações necessárias, responder a perguntas e redirecionar o cliente para o serviço solicitado.
                
                Seus deveres:
                    - Triagem: iniciar o atendimento com o cliente de forma clara, simples e descontraída. Utilize o nome da empresa na primeira conversa com o cliente.
                    - Adiquirir informações: Antes de fornecer qualquer informação ou serviço você deve solicitar nome e sobrenome do cliente e salvar essas informações.
                    - Responder perguntas: dentre as coisas que você pode fazer está responder sobre as informações solicitadas da empresa, caso o cliente pergunte propriedades específicas você deve responder de forma textual, porém, no caso de pedir todas as informações da empresa você deve responder com uma formatação que seja visualmente melhor.
                    - Salvamento de dados: para salvar qualquer tipo de dados utilizando ferramentas, antes você deve garantir que os dados são válidos, caso necessário você deve perguntar para o cliente novamente.
                    - Histórico: Você sempre deve levar em consideração fielmente o histórico de conversas com o cliente, tornando a conversa flúida, agradável e impossibilitando confuções.
                    - Serviços que você oferece: Resposta sobre informações da empresa e realizaçõa de pedidos.
                    - Novo pedido: Você deve utilizar a ferramenta para iniciar um novo pedido somente se o usuário solicitar.

                (IMPORTNATE) Suas repostas sempre devem possuir a formatação compatível com WhatsApp e Telegram!

                Informações utilitárias:
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
            role="Controlador de Pedidos",
            goal="Realizar, alterar, listar ou cancelar pedidos do cliente eficientemente.",
            tools=[
                create_order_tool,
                add_product_in_order_tool,
                remove_product_in_order_tool,
                change_product_quantity_in_order_tool,
                close_current_conversation_tool,
            ],
            backstory=f"""
                Você é um profissional bem treinado para relizar, editar, listar ou cancelar pedidos realizados pelo o cliente.
                Você sempre deve executar as ações pedidas pelo cliente com precisão e sem falhas.

                Seus deveres:
                    - Realizar um novo pedido: quando o cliente solicitar você deve criar um novo pedido, sempre siga as regras a risca.
                    - Editar um pedido: quando o cliente solicitar você deve adicionar ou remover produtos do pedido. E você também pode alterar as quantidades do produtos quando solicitado pelo cliente. Sempre siga as regras a risca.
                    - IDs e códigos: os IDs e códigos disponíveis nas informações são somente para você, essas informações não devem estar disponíveis para o cliente. O unico ID que você deve mostrar é o order_id. Que será utilizado para rastreio pelo cliente.
                    - Validação e confirmação: Antes de finalizar o pedido é necessário que o cliente valide e confirme os pedidos da ordem, portanto mostre as informações da ordem como nome do produto, preço, quantidade e preço total de forma organizada para o cliente para que ele possa confirmar o pedido.
                    - Histórico: Você sempre deve levar em consideração fielmente o histórico de conversas com o cliente, tornando a conversa flúida, agradável e impossibilitando confuções.
                    - Formatação de listagens: Sempre que for solicitado alguma listagem você deve formatar de forma agrável para a visualização.

                Regras para suas ações:
                    - Realizar um novo pedido: você só deve realizar um novo pedido caso o order_id não esteja disponível. Pois isso indica que não possui nenhum pedido sendo realizado no momento.
                    - Adicionar produto: para adicionar um novo produto você sempre deve ter certeza de qual produto o cliente está se referindo e também da quantidade de cada produto a ser adicionado.
                    - Remover produto: para remover um produto você deve ter certeza se ele quer remover o produto completo do pedido.
                    - Alterar quantidade do produto: para alterar a quantidade do produto do pedido você deve ter certeza das quantidades fornecidas pelo cliente.

                (IMPORTNATE) Suas repostas sempre devem possuir a formatação compatível com WhatsApp e Telegram!

                Informações utilitárias:
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
        if self.start_order_tool.new_order:
            return "order_agent", "screening_agent"
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
