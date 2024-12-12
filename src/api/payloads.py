from pydantic import BaseModel


class WhatsappPayloadKey(BaseModel):
    remoteJid: str


class WhatsappPayloadAudioMessage(BaseModel):
    url: str


class WhatsAppPayloadMessage(BaseModel):
    conversation: str | None = None
    audioMessage: WhatsappPayloadAudioMessage | None = None
    base64: str | None = None


class WhatsappPayloadData(BaseModel):
    key: WhatsappPayloadKey
    message: WhatsAppPayloadMessage


class WhatsappPayload(BaseModel):
    data: WhatsappPayloadData
