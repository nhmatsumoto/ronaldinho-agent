import json
import os
import base64
from config import settings
import logging

logger = logging.getLogger("token-vault")

class TokenVault:
    def __init__(self):
        self.vault_path = os.path.join(settings.DATA_DIR, "vault.json")
        self._ensure_dir()
        self.secret_key = settings.GEMINI_API_KEY[:16] if settings.GEMINI_API_KEY else "ronaldinho-secret"

    def _ensure_dir(self):
        os.makedirs(settings.DATA_DIR, exist_ok=True)
        if not os.path.exists(self.vault_path):
            with open(self.vault_path, "w") as f:
                json.dump({}, f)

    def _xor_cipher(self, data: str) -> str:
        """Simple XOR cipher for basic token protection on disk."""
        return "".join(chr(ord(c) ^ ord(self.secret_key[i % len(self.secret_key)])) for i, c in enumerate(data))

    def save_token(self, provider: str, token_data: dict):
        try:
            with open(self.vault_path, "r") as f:
                vault = json.load(f)
            
            raw_data = json.dumps(token_data)
            encrypted_data = base64.b64encode(self._xor_cipher(raw_data).encode()).decode()
            
            vault[provider] = encrypted_data
            
            with open(self.vault_path, "w") as f:
                json.dump(vault, f)
            logger.info(f"Token saved for provider: {provider}")
        except Exception as e:
            logger.error(f"Failed to save token to vault: {e}")

    def get_token(self, provider: str) -> dict:
        try:
            with open(self.vault_path, "r") as f:
                vault = json.load(f)
            
            if provider not in vault:
                return None
            
            encrypted_data = vault[provider]
            decoded_data = base64.b64decode(encrypted_data).decode()
            raw_data = self._xor_cipher(decoded_data)
            
            return json.loads(raw_data)
        except Exception as e:
            logger.error(f"Failed to read token from vault: {e}")
            return None

    def list_providers(self):
        try:
            with open(self.vault_path, "r") as f:
                vault = json.load(f)
            return list(vault.keys())
        except Exception:
            return []

# Singleton instance
vault = TokenVault()
