from pydantic_settings import BaseSettings

class Config(BaseSettings):
    db_url: str
    openai_api_key: str
    gemini_api_key: str
    evolution_api_key: str
    whatsapp_send_message_url: str

    class Config:
        env_file = ".env"

config = Config()