import os
import requests
import json
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), '.env'))
api_key = os.getenv('GEMINI_API_KEY')

models_to_test = [
    "gemini-2.0-flash-lite-preview-02-05",
    "gemini-2.0-flash-exp",
    "gemini-1.5-pro-latest"
]

versions_to_test = ["v1beta", "v1"]

for model in models_to_test:
    for version in versions_to_test:
        url = f"https://generativelanguage.googleapis.com/{version}/models/{model}:generateContent?key={api_key}"
        print(f"Testing {model} on {version}...")
        
        payload = {
            "contents": [{"parts": [{"text": "Hei"}]}]
        }
        
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                print(f"✅ SUCCESS: {model} on {version}")
                # print(response.text[:100])
                break # Found one that works for this model?
            else:
                print(f"❌ FAIL ({response.status_code}): {model} on {version}")
        except Exception as e:
            print(f"❌ ERROR: {e}")
