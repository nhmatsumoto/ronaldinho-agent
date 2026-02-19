import sys
import json

def chat_response(message):
    return message

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: gemini.py chat \"mensagem\"")
        sys.exit(1)
        
    cmd = sys.argv[1].lower()
    if cmd == "chat" and len(sys.argv) >= 3:
        print(chat_response(sys.argv[2]))
    else:
        print("Acao nao suportada.")
