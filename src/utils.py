import json
from src.database import Client, ClientConversation, Company, Order, Product


def create_history_informations(conversations: list[ClientConversation]) -> str:
    formatted = "\n".join([f"cliente: {item.input}\nvocê: {item.output}" for item in conversations])
    return """
    Histórico de conversas:
    {history}

    """.format(
        history=formatted
    )


def create_company_informations(company: Company):
    company_dict = company.model_dump()
    company_info = "Dados da empresa\n"
    for key, value in company_dict.items():
        company_info += f" - {key}: {value}\n"
    return company_info


def create_client_informations(client: Client):
    return f"""
    Dados do cliente
     - nome: {client.first_name if client.first_name else "Não informado."}
     - sobrenome: {client.last_name if client.last_name else "Não informado."}

    """


def create_products_list(products: list[Product]) -> str:
    products_info = "PRODUTOS\n"
    products_dict = []
    for product in products:
        product_dict = product.model_dump()
        product_dict["product_id"] = product_dict.pop("id")
        products_dict.append(product_dict)
    products_info += json.dumps(products_dict)
    products_info += "\n"
    return products_info


def create_order_informations(order: Order | None) -> str:
    order_info = "INFORMAÇÕES DA ORDEM\n"
    order_info += f' order_id: {order.id if order else "Não criado"}\n'
    order_info += f' - Status: {order.status if order else "products_dict"}\n'
    order_info += f" - Valor total: {order.total if order else 0.0}\n"
    order_info += f" - Endereço de entrega: {order.address if order and order.address else "Não informado"}\n"

    if order:
        products_dict = []
        for order_product in order.products:
            product_dict = order_product.model_dump()
            product_dict["order_product_id"] = product_dict.pop("id")
            products_dict.append(product_dict)
        order_info += " - Produtos da ordem\n"
        order_info += json.dumps(products_dict)
        order_info += "\n"
    return order_info
