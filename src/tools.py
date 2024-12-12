from typing import Any
from crewai.tools import BaseTool

from src.database import Client
from src.services import Services


class SaveClientNamesTool(BaseTool):
    name: str = "Ferramenta de salvar nome de cliente"
    description: str = "Ferramenta útil para salvar nome e sobrenome do usuário na base de dados."
    services: Services
    client: Client

    def _run(self, first_name: str, last_name: str):
        self.services.save_client_names(self.client, first_name, last_name)

    class Config:
        arbitrary_types_allowed = True

class StartOrder(BaseTool):
    name: str = 'Ferramenta para iniciar um novo pedido.'
    description: str = 'Ferramenta util para iniciar um novo pedido para o cliente'
    new_order: bool = False
    

    def _run(self):
        self.new_order = True

    class Config:
        arbitrary_types_allowed = True


class CreateOrderTool(BaseTool):
    name: str = "Ferramenta para criar um pedido"
    description: str = "Ferramenta util para criar o pedido em que vão ser anexado os produtos"
    services: Services
    client: Client

    def _run(self):
        self.services.create_order(self.client)

    class Config:
        arbitrary_types_allowed = True


class AddProductInOrderTool(BaseTool):
    name: str = "Ferramenta para adicionar produto ao pedido"
    description: str = (
        "Ferramenta util para adicionar produtos em uma ordem já existente, order_id, product_id e quantity como parametros."
    )
    services: Services
    client: Client

    def _run(self, order_id: int, product_id: int, quantity: int):
        return self.services.add_product_to_order(order_id, product_id, quantity)

    class Config:
        arbitrary_types_allowed = True


class RemoveProductInOrderTool(BaseTool):
    name: str = "Ferramenta para remover produto do pedido"
    description: str = "Ferramenta util para remover produto do pedido em uma ordem já existente"
    services: Services
    client: Client

    def _run(self, order_product_id: int):
        return self.services.remove_product_from_order(order_product_id)

    class Config:
        arbitrary_types_allowed = True


class ChangeProductQuantityInOrderTool(BaseTool):
    name: str = "Ferramenta para trocar a quantidade de produtos do pedido"
    description: str = "Ferramenta util para alterar a quantidade de produtos de um produto de uma ordem já existente."
    services: Services
    client: Client

    def _run(self, order_product_id: int, quantity: int):
        self.services.update_product_quantity(order_product_id, quantity)

    class Config:
        arbitrary_types_allowed = True


class CloseCurrentConversation(BaseTool):
    name: str = "Ferramenta para encerrar a conversa atual"
    description: str = "Ferramenta util para encerrar a conversa atual."
    services: Services
    client: Client

    def _run(self):
        self.services.close_current_conversation(self.client)

    class Config:
        arbitrary_types_allowed = True