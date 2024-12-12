from sqlmodel import Session, select

from src.database import Client, ClientConversation, Company, Order, OrderProduct, Product


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
            .outerjoin(ClientConversation, Client.id == ClientConversation.client_id)
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

    def create_order(self, client: Client) -> Order:
        order = Order(client=client)
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        return order

    def get_order_by_client(self, client: Client) -> Order | None:
        return self.session.exec(
            select(Order)
            .outerjoin(OrderProduct, OrderProduct.order_id == Order.id)
            .where(Order.client_id == client.id)
        ).first()

    def add_product_to_order(self, order_id: int, product_id: int, quantity: int) -> OrderProduct:
        product = self.session.get(Product, product_id)
        order_product = OrderProduct(order_id=order_id, product_id=product_id, quantity=quantity, price=product.price)
        self.session.add(order_product)
        self.session.commit()
        self.session.refresh(order_product)
        return order_product

    def remove_product_from_order(self, order_product_id: int):
        order_product = self.session.get(OrderProduct, order_product_id)
        self.session.delete(order_product)

    def update_product_quantity(self, order_product_id: int, quantity: int):
        order_product = self.session.get(OrderProduct, order_product_id)
        order_product.quantity = quantity
        self.session.commit()

    def get_client_conversation(self, client: Client):
        return self.session.exec(
            select(ClientConversation).where(
                (ClientConversation.client_id == client.id) & (ClientConversation.closed == False)
            )
        ).all()

    def close_current_conversation(self, client: Client):
        for conversation in self.get_client_conversation(client):
            conversation.closed = True
        self.session.commit()
