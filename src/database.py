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

    orders: list["Order"] = Relationship(back_populates="product")


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

    client: Client = Relationship(back_populates="conversations")


class Order(SQLModel, SQLModelBase, table=True):
    client_id: int = Field(foreign_key="client.id")
    product_id: int = Field(foreign_key="product.id")
    price: float = Field(decimal_places=2)
    quantity: int = Field()
    status: str = Field(default="open")

    client: Client = Relationship(back_populates="orders")
    product: Product = Relationship(back_populates="orders")

    @property
    def total(self) -> float:
        return round(self.price * self.quantity, 2)


engine = create_engine(config.db_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
