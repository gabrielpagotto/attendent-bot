import logging
from crewai import Agent, Crew, Process, Task, LLM
from langchain_community.chat_models import ChatOpenAI
from config import config

from src import utils
from src import tools
from src.services import Services
from src.database import Client


def transcript_audio_to_text_with_agent(audio_file_url: str):

    file_read_tool = tools.ReadFileCustomTool(file_path=audio_file_url)
    logging.basicConfig(level=logging.DEBUG)

    agent = Agent(
        role="Transcritor de áudio",
        goal="Transcrever arquivos de áudios para texto.",
        verbose=True,
        backstory="Você é um profissional em transcrever arquivos de áudio, utilize a ferramenta de ler arquivos para obter o arquivo de áudio a ser transcrito. Caso aconteça algum erro, mostre o erro.",
        tools=[file_read_tool],
    )
    task = Task(
        description=f"Quero obter o texto do áudio fornecido",
        expected_output="Texto do conteúdo do áudio",
        agent=agent,
    )
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        llm=LLM(model="gemini/gemini-1.5-flash", api_key=config.gemini_api_key),
    )
    crew.kickoff()
    return task.output.raw


class ClientAttendent:

    def __init__(self, services: Services, client: Client) -> None:
        self.services = services
        self.client = client
        self.conversations = self.services.get_client_conversation(client)

        self.company = self.services.get_company()
        self.products = self.services.get_products()

        self.client_informations = utils.create_client_informations(self.client)
        self.history_informations = utils.create_history_informations(self.conversations)
        self.company_informations = utils.create_company_informations(self.company)

        self.start_order_tool = tools.StartOrder()
        self.save_client_names_tool = tools.SaveClientNamesTool(services=self.services, client=self.client)
        self.close_current_conversation_tool = tools.CloseCurrentConversation(
            services=self.services, client=self.client
        )

        self.order = services.get_order_by_client(self.client)

        self.products_informations = utils.create_products_list(self.products)
        self.order_informations = utils.create_order_informations(self.order)

        self.create_order_tool = tools.CreateOrderTool(services=services, client=client)
        self.add_product_in_order_tool = tools.AddProductInOrderTool(services=services, client=client)
        self.remove_product_in_order_tool = tools.RemoveProductInOrderTool(services=services, client=client)
        self.change_product_quantity_in_order_tool = tools.ChangeProductQuantityInOrderTool(
            services=services, client=client
        )
        self.save_order_address_tool = tools.SaveOrderAddress(services=self.services, client=self.client)
        self.finalize_order_tool = tools.FinalizeOrder(services=self.services, client=self.client)
        self.get_address_from_cep_tool = tools.GetAddressFromCepTool()

        self.screening_agent = Agent(
            name="Agente de triagem",
            role="Realizar a triagem, conhecer o cliente, responder perguntas e redirecionar para outros serviços",
            goal="Realizar a triagem do cliente de forma adqueda e adiquirir informações, responder perguntas e redirecionar para os serviços mais adequados",
            tools=[self.start_order_tool, self.save_client_names_tool, self.close_current_conversation_tool],
            backstory=f"""

                Você é um profissional para realizar o primeiro contato com o cliente e seu dever é realizar a triagem de forma adequada, adiquirindo informações necessárias, responder a perguntas e redirecionar o cliente para o serviço solicitado.
                
                Seus deveres (Trate na sequencia como prioridade):
                    - Triagem: iniciar o atendimento com o cliente de forma clara, simples e descontraída. Utilize o nome da empresa na primeira conversa com o cliente.
                    - Adiquirir informações: Antes de fornecer qualquer informação ou serviço você deve solicitar nome e sobrenome do cliente e salvar essas informações.
                    - Responder perguntas: dentre as coisas que você pode fazer está responder sobre as informações solicitadas da empresa, caso o cliente pergunte propriedades específicas você deve responder de forma textual, porém, no caso de pedir todas as informações da empresa você deve responder com uma formatação que seja visualmente melhor.
                    - Salvamento de dados: para salvar qualquer tipo de dados utilizando ferramentas, antes você deve garantir que os dados são válidos, caso necessário você deve perguntar para o cliente novamente.
                    - Histórico: Você sempre deve levar em consideração fielmente o histórico de conversas com o cliente, tornando a conversa flúida, agradável e impossibilitando confuções.
                    - Serviços que você oferece: Resposta sobre informações da empresa e realizaçõa de pedidos.
                    - Novo pedido: Você deve utilizar a ferramenta para iniciar um novo pedido somente se o usuário solicitar.

                (IMPORTNATE) Suas repostas sempre devem possuir a formatação compatível com WhatsApp e Telegram!
                (IMPORTANTE) Você só deve conluir a conversa se o cliente pedir para reiniciar a conversa ou se ele não tiver mais nenhuma solicitação para você!

                Informações utilitárias:
                {self.client_informations}
                {self.history_informations}
                {self.company_informations}
            """,
        )

        self.order_agent = Agent(
            role="Controlador de Pedidos",
            goal="Realizar, alterar, listar ou cancelar pedidos do cliente eficientemente.",
            tools=[
                self.create_order_tool,
                self.add_product_in_order_tool,
                self.remove_product_in_order_tool,
                self.change_product_quantity_in_order_tool,
                self.close_current_conversation_tool,
                self.save_order_address_tool,
                self.finalize_order_tool,
                self.get_address_from_cep_tool,
            ],
            backstory=f"""
                Você é um profissional bem treinado para relizar, editar, listar ou cancelar pedidos realizados pelo o cliente.
                Você sempre deve executar as ações pedidas pelo cliente com precisão e sem falhas.

                Seus deveres (Trate na sequencia como prioridade):
                    - Criação de pedido: Caso o order_id não exista, você deve criar um novo pedido para ser preenchido com os produtos posteriomente.
                    - Realizar um novo pedido: quando o cliente solicitar você deve criar um novo pedido, sempre siga as regras a risca.
                    - Editar um pedido: quando o cliente solicitar você deve adicionar ou remover produtos do pedido. E você também pode alterar as quantidades do produtos quando solicitado pelo cliente. Sempre siga as regras a risca.
                    - IDs e códigos: os IDs e códigos disponíveis nas informações são somente para você, essas informações não devem estar disponíveis para o cliente. O unico ID que você deve mostrar é o order_id. Que será utilizado para rastreio pelo cliente. Sempre siga as regras a risca.
                    - Histórico: Você sempre deve levar em consideração fielmente o histórico de conversas com o cliente, tornando a conversa flúida, agradável e impossibilitando confuções. Sempre siga as regras a risca.
                    - Pedir endereço de entrega: você deve pedir para que o usuário informe o endereço completo ou que ele informe o CEP, caso ele informe somente o cep você deve utilizar a ferramenta de busca de endereços pelo CEP para buscar o endereço pelo CEP fornecido. Sempre siga as regras a risca.
                    - Validação: O pedido não deve ser salvo de forma alguma sem que o cliente informe os produtos, endereço de entrega.
                    - Formatação de listagens: Sempre que for solicitado alguma listagem você deve formatar de forma agrável para a visualização. Sempre siga as regras a risca.

                Regras para suas ações:
                    - Realizar um novo pedido: você só deve realizar um novo pedido caso o order_id não esteja disponível. Pois isso indica que não possui nenhum pedido sendo realizado no momento.
                    - Adicionar produto: para adicionar um novo produto você sempre deve ter certeza de qual produto o cliente está se referindo e também da quantidade de cada produto a ser adicionado.
                    - Remover produto: para remover um produto você deve ter certeza se ele quer remover o produto completo do pedido.
                    - Alterar quantidade do produto: para alterar a quantidade do produto do pedido você deve ter certeza das quantidades fornecidas pelo cliente.
                    - Pedir endereço de entrega: Você somente deve pedir o endereço de entrega após ser finalizado a seleção de produtos.
                    - Conclusão do pedido: Se estiver sem endereço, o pedido não deve ser salvo, peça que o cliente informe o endereço.

                A ordem que você deve seguir para realizar o pedido é [criação do pedido>edição de produtos>confirmação de produtos>endereço de entrega>confirmação]. Nunca faça em outra ordem!

                (IMPORTNATE) Suas repostas sempre devem possuir a formatação compatível com WhatsApp e Telegram!
                (IMPORTANTE) Você só deve fechar a conversa se o cliente pedir isso ou quando finalizar o pedido!

                Informações utilitárias:
                {self.client_informations}
                {self.history_informations}
                {self.products_informations}
                {self.order_informations}
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

    def run(self, task: Task) -> tuple[str, str, bool]:
        agents = ["screening_agent", "order_agent"]
        using_agent = self.conversations[-1].agent if len(self.conversations) > 0 else agents[0]
        while using_agent is not None and using_agent in agents:
            output, agent = {
                agents[0]: self._execute_screening_agent(task),
                agents[1]: self._execute_order_agent(task),
            }[using_agent]

            if output not in agents:
                return output, agent, self.close_current_conversation_tool.to_close
            using_agent = output
