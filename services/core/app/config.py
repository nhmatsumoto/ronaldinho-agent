import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))

class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    NVIDIA_API_KEY: str = ""
    NVIDIA_MODEL_ID: str = "meta/llama-3-1-8b-instruct"
    GROQ_API_KEY: str = ""
    
    # Expanded Free Model Providers
    CEREBRAS_API_KEY: str = ""
    SAMBANOVA_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    MISTRAL_API_KEY: str = ""
    SCALEWAY_API_KEY: str = ""
    HYPERBOLIC_API_KEY: str = ""
    
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    TELEGRAM_BOT_TOKEN: str = ""
    LLM_PROVIDER: str = "gemini" # Default provider
    MODEL_PRIORITY: str = "gemini,nvidia,openai,anthropic,groq,cerebras,sambanova,openrouter,mistral"
    CODING_MODEL_ID: str = "nvidia:meta/llama-3.1-405b-instruct"
    ENABLE_BENCHMARKING: bool = True
    PORT: int = 5000
    DATA_DIR: str = "ronaldinho"

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
