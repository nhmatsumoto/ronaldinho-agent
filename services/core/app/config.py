import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    NVIDIA_API_KEY: str = ""
    TELEGRAM_BOT_TOKEN: str = ""
    LLM_PROVIDER: str = "gemini"
    PORT: int = 5000
    DATA_DIR: str = "ronaldinho"

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
