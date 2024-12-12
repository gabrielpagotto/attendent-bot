from fastapi import APIRouter, Depends
from crewai import Task

from src.agents.manager_agent import ScreeningAgent
from src.api.dependencies import get_services
from src.api.payloads import Message
from src.services import Services

api_router = APIRouter(prefix="/api/v1")


@api_router.post("/message")
async def message(message: Message, services: Services = Depends(get_services)):
    client = services.get_or_create_client(message.user_id)

    task = Task(
        description=message.message,
        expected_output="Resposta curta e direta que direciona o cliente para o próximo passo.",
    )

    task_processor = ScreeningAgent(services, client)

    output, agent = task_processor.run(task)
    services.add_client_conversation(client, message.message, output, agent)

    return {"message": output}
