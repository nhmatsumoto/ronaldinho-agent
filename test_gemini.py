import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API Key not found in .env")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-flash-latest")

print(f"Testing Gemini 1.5 Flash with key: {api_key[:10]}...")
try:
    response = model.generate_content("Oi")
    print("Response Success!")
    print(response.text)
except Exception as e:
    print("Gemini Test Failed:")
    print(str(e))
