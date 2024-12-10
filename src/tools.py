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
