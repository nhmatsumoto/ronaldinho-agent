import os
import requests
import json
from dotenv import load_dotenv

# Load .env manually to be sure
load_dotenv(os.path.join(os.getcwd(), '.env'))

api_key = os.getenv('GEMINI_API_KEY')
model = "gemini-1.5-flash"
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

print(f"Testing URL: https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent")

payload = {
    "contents": [{
        "parts": [{"text": "Hello, are you alive?"}]
    }]
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
