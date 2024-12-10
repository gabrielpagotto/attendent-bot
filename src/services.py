from sqlmodel import Session, select

from src.database import Client, ClientConversation, Company, Product


class Services:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_company(self) -> Company:
        return self.session.exec(select(Company)).first()

    def get_products(self) -> list[Product]:
        return self.session.exec(select(Product)).all()

    def get_or_create_client(self, phone_number: str) -> Client:
        client = self.session.exec(
            select(Client)
            .join(ClientConversation, ClientConversation.client_id == Client.id)
            .where(Client.phone_number == phone_number)
        ).first()
        if not client:
            client = Client(phone_number=phone_number)
            self.session.add(client)
            self.session.commit()
            self.session.refresh(client)
        return client

    def add_client_conversation(self, client: Client, input: str, output: str, agent: str) -> ClientConversation:
        conversation = ClientConversation(client=client, input=input, output=output, agent=agent)
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def save_client_names(self, client: Client, first_name: str | None, last_name: str | None):
        client.first_name = first_name
        client.last_name = last_name
        self.session.commit()
