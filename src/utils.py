from src.database import Client, ClientConversation, Company


def create_history_listing(conversations: list[ClientConversation]) -> str:
    formatted = "\n".join([f"user: {item.input}\nassistent: {item.output}" for item in conversations])
    return """
    Seu histórico de conversa com o cliente é:
    {history}

    """.format(
        history=formatted
    )


def create_company_listing(company: Company):
    company_dict = company.model_dump()
    company_info = "DADOS DA EMPRESA\n"
    for key, value in company_dict.items():
        company_info += f" - {key}: {value}\n"
    return company_info


def create_client_informations(client: Client):
    return f"""
    INFORMAÇÕES DO CLIENTE
     - nome: {client.first_name if client.first_name is not None else "Não informado."}
     - sobrenome: {client.last_name if client.last_name is not None else "Não informado."}

    """
