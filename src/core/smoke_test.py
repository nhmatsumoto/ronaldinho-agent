import httpx
import asyncio

async def smoke_test():
    url = "http://localhost:5000/api/chat"
    payload = {
        "message": "Ronaldinho, adote a Arquitetura Manus: escreva um script python chamado 'hello_manus.py' que imprima a versão do python e a data atual, execute-o e me mostre o resultado final do terminal.",
        "user_id": "test_user"
    }
    
    print("[*] Sending smoke test message to Python Neural Core...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=60)
            if response.status_code == 200:
                print("✅ Success! Response:")
                print(response.json().get("response"))
            else:
                print(f"❌ Failed: {response.status_code}")
                print(response.text)
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")

if __name__ == "__main__":
    print("Note: Ensure Neural Core is running on port 5000 before starting this test.")
    # asyncio.run(smoke_test()) # Uncomment to run manually
