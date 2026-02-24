import httpx
import os
import logging
from config import settings
from vault import vault

logger = logging.getLogger("auth-manager")

class OAuthManager:
    def __init__(self):
        # Mocking credentials for demonstration, normally these come from .env
        self.providers = {
            "google": {
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "client_id": os.getenv("GOOGLE_CLIENT_ID", "mock-id"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", "mock-secret"),
                "scope": "https://www.googleapis.com/auth/generative-language"
            },
            "openai": {
                "auth_url": "https://auth.openai.com/authorize",
                "token_url": "https://api.openai.com/1/oauth/token",
                "client_id": os.getenv("OPENAI_CLIENT_ID", "mock-id"),
                "client_secret": os.getenv("OPENAI_CLIENT_SECRET", "mock-secret"),
                "scope": "user.read"
            }
        }

    def get_login_url(self, provider: str, redirect_uri: str) -> str:
        config = self.providers.get(provider)
        if not config:
            return None
        
        if config['client_id'] == "mock-id" or config['client_secret'] == "mock-secret":
            raise ValueError(f"As credenciais OAuth para {provider} não foram configuradas no .env. Configure GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET.")
            
        return f"{config['auth_url']}?client_id={config['client_id']}&redirect_uri={redirect_uri}&response_type=code&scope={config['scope']}&access_type=offline&prompt=consent"

    async def exchange_code(self, provider: str, code: str, redirect_uri: str):
        config = self.providers.get(provider)
        if not config:
            return None

        logger.info(f"Exchanging code for {provider} token...")
        
        mock_token = {
            "access_token": f"mock-{provider}-access-token-{code[:8]}",
            "refresh_token": f"mock-{provider}-refresh-token",
            "expires_in": 3600
        }
        
        vault.save_token(provider, mock_token)
        return mock_token

auth_manager = OAuthManager()
