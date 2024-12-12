import requests
from crewai.tools import BaseTool
from crewai_tools import FileReadTool

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
    name: str = "Ferramenta para iniciar um novo pedido."
    description: str = "Ferramenta util para iniciar um novo pedido para o cliente"
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


class SaveOrderAddress(BaseTool):
    name: str = "Ferramenta salvar o endereço em que o pedido deve ser entre"
    description: str = "Ferramenta util salvar o endereço em que o pedido deve ser entre."
    services: Services
    client: Client

    def _run(self, order_id: int, address: str):
        self.services.save_order_address(order_id, address)

    class Config:
        arbitrary_types_allowed = True


class FinalizeOrder(BaseTool):
    name: str = "Ferramenta confirmar o pedido"
    description: str = "Ferramenta util confirmar o pedido."
    services: Services
    client: Client

    def _run(self, order_id: int):
        self.services.finalized_order(order_id)

    class Config:
        arbitrary_types_allowed = True

class GetAddressFromCepTool(BaseTool):
    name: str = 'Ferramenta para buscar endereço pelo CEP'
    description: str = 'Ferramenta util para buscar um endereço completo com base no CEP fornecido.'

    def _run(self, cep: str) -> str:
        cep = cep.replace("-", "").strip()
        if not cep.isdigit() or len(cep) != 8:
            return "CEP inválido. O CEP deve conter exatamente 8 dígitos numéricos."        
        url = f"https://viacep.com.br/ws/{cep}/json/"        
        try:
            response = requests.get(url)
            response.raise_for_status()            
            data = response.json()            
            if "erro" in data:
                return f"Endereço não encontrado para o CEP: {cep}."            
            return (
                f"{data.get('logradouro', 'Logradouro não disponível')}, "
                f"{data.get('bairro', 'Bairro não disponível')}, "
                f"{data.get('localidade', 'Cidade não disponível')} - "
                f"{data.get('uf', 'UF não disponível')}"
            )
        
        except requests.exceptions.RequestException as e:
            return f"Erro ao buscar o endereço: {str(e)}"


class CloseCurrentConversation(BaseTool):
    name: str = "Ferramenta para encerrar a conversa atual"
    description: str = "Ferramenta util para encerrar a conversa atual."
    services: Services
    client: Client
    to_close: bool = False

    def _run(self):
        self.to_close = True

    class Config:
        arbitrary_types_allowed = True

class ReadFileCustomTool(FileReadTool):
    
    def _run(self, **kwargs):
        try:
            file_path = kwargs.get("file_path", self.file_path)
            with open(file_path, "rb") as file:
                return file.read()
        except Exception as e:
            return f"Fail to read the file {file_path}. Error: {e}"