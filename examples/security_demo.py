import os
import sys
from pathlib import Path

# Fix path to allow importing from ronaldinho/skills
WORKSPACE_ROOT = Path(__file__).parents[1]
sys.path.append(str(WORKSPACE_ROOT))

from ronaldinho.skills.security_tool import encrypt_data, generate_key
from ronaldinho.skills.security_scrub_tool import scrub_content

def demo_security():
    print("🛡️  Ronaldinho Security & Scrubbing Demo\n")
    
    # 1. Encryption
    print("--- 1. Encryption Proof ---")
    print("Scenario: Encrypting a simulated API Key locally.")
    
    # We'll use a dummy key for this demo as we don't want to print a fresh one every time
    # but the utility is there.
    dummy_key = "L7eN8XoGv3XUu8p-pU_U_9y7n6pU1w2x3y4z5a6b7c8=" # Form-factor only
    secret_data = "GEMINI_API_KEY=sk-ant-1234567890abcdef"
    
    # In a real scenario, use generate_key()
    print(f"Original Data: {secret_data}")
    encrypted = encrypt_data(secret_data, dummy_key)
    print(f"Encrypted Blob: {encrypted}")
    print("✅ Result: Data is unreadable without the local private key.\n")

    # 2. Scrubbing
    print("--- 2. Log Scrubbing Proof ---")
    print("Scenario: Sanitizing a raw log entry before storage.")
    
    raw_log = "Agent Orquestrador: processing request for user hiroyuki@example.com using key sk-1234567890abcdefghij"
    print(f"Raw Content: {raw_log}")
    
    scrubbed = scrub_content(raw_log)
    print(f"Scrubbed Content: {scrubbed}")
    print("✅ Result: Email and API Key were automatically redacted.")

if __name__ == "__main__":
    demo_security()
