from sqlmodel import Field, SQLModel, Relationship, create_engine

from config import config


class SQLModelBase:
    id: int | None = Field(default=None, primary_key=True)


class Company(SQLModel, SQLModelBase, table=True):
    name: str = Field()
    address: str = Field()
    cep: str = Field()
    email: str = Field()
    phone_number: str = Field()
    whatsapp: str = Field()
    instagram: str = Field()
    cnpj: str = Field()
    opening_hours: str = Field()


class Product(SQLModel, SQLModelBase, table=True):
    description: str = Field()
    price: float = Field(decimal_places=2)
    code: str = Field()


class Client(SQLModel, SQLModelBase, table=True):
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    phone_number: str = Field(index=True)
    address: str | None = Field(default=None)

    orders: list["Order"] = Relationship(back_populates="client")
    conversations: list["ClientConversation"] = Relationship(back_populates="client")


class ClientConversation(SQLModel, SQLModelBase, table=True):
    input: str = Field()
    output: str = Field()
    agent: str = Field()
    client_id: int = Field(foreign_key="client.id")
    closed: bool = Field(default=False)

    client: Client = Relationship(back_populates="conversations")


class Order(SQLModel, SQLModelBase, table=True):
    client_id: int = Field(foreign_key="client.id")
    status: str = Field(default="open")

    client: Client = Relationship(back_populates="orders")
    products: list["OrderProduct"] = Relationship(back_populates="order")

    @property
    def total(self) -> float:
        total = 0.0
        for product in self.products:
            total += round(product.price * product.quantity, 2)
        return round(total, 2)


class OrderProduct(SQLModel, SQLModelBase, table=True):
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    price: float = Field(decimal_places=2)
    quantity: int = Field()

    order: Order = Relationship(back_populates="products")


engine = create_engine(config.db_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
