from fastapi import APIRouter, Depends
from crewai import Task

from src.agents.manager_agent import TaskProcessor
from src.api.dependencies import get_services
from src.api.payloads import Message
from src.services import Services

api_router = APIRouter(prefix="/api/v1")


@api_router.post("/message")
async def message(message: Message, services: Services = Depends(get_services)):
    company = services.get_company()
    products = services.get_products()
    client = services.get_or_create_client(message.user_id)

    task = Task(
        description=message.message,
        expected_output="Resposta curta e direta que direciona o cliente para o próximo passo.",
    )

    task_processor = TaskProcessor(task, services, client)

    output = task_processor.process_task()
    services.add_client_conversation(client, message.message, output, "first_contact_agent")

    return {"message": output}
