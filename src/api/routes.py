import os, requests, base64, uuid

from fastapi import APIRouter, Depends
from crewai import Task

from config import config
from src.agents import ClientAttendent, transcript_audio_to_text_with_agent
from src.api.dependencies import get_services
from src.api.payloads import WhatsappPayload
from src.services import Services

api_router = APIRouter(prefix="/api/v1")


@api_router.post("/evolution-api/webhook")
async def message(payload: WhatsappPayload, services: Services = Depends(get_services)):
    client = services.get_or_create_client(payload.data.key.remoteJid)

    text = payload.data.message.conversation

    if payload.data.message.conversation:
        text = payload.data.message.conversation
    elif payload.data.message.audioMessage.url:
        os.makedirs("audios", exist_ok=True)

        base64_audio = payload.data.message.base64
        base64_audio = base64_audio.replace("\n", "")

        audio_data = base64.b64decode(base64_audio, validate=True)
        filename = f"audios/audio_{uuid.uuid4()}.mp3"

        with open(filename, "wb") as audio_file:
            audio_file.write(audio_data)

        text = transcript_audio_to_text_with_agent(filename)
    else:
        return {"error": "Payload not have and conversation or audio message."}, 400

    task = Task(
        description=text,
        expected_output="Resposta curta e direta que direciona o cliente para o próximo passo.",
    )

    task_processor = ClientAttendent(services, client)

    output, agent, close_conversation = task_processor.run(task)
    services.add_client_conversation(client, text, output, agent)

    if close_conversation:
        # Disabled for now
        # services.close_current_conversation(client)
        ...

    try:
        response = requests.post(
            config.whatsapp_send_message_url,
            json={"number": payload.data.key.remoteJid, "text": output},
            headers={"Content-Type": "application/json", "apikey": config.evolution_api_key},
        )
        response.raise_for_status()
        return {"success": f"Response sended to {payload.data.key.remoteJid}"}
    except requests.RequestException as e:
        return {"error": "Failed to send the response to the user", "trace": e}, 400
