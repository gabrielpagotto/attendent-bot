from pydantic_settings import BaseSettings

class Config(BaseSettings):
    db_url: str
    openai_api_key: str
    anthropic_api_key: str

    class Config:
        env_file = ".env"

config = Config()