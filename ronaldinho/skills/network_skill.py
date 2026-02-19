import os
import sys
import subprocess
import json

def run_curl(url, method="GET", params=None):
    cmd = ["curl", "-X", method, url]
    if params:
        # Simplistic params handling for now
        cmd += ["-d", json.dumps(params)]
        
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Erro ao executar curl: {e}"

def oauth_flow(service):
    # This is a placeholder for a real OAuth flow
    # In a CLI agent, we typically output a URL and wait for a token
    if service.lower() == "google":
        return "Simulacao OAuth Google: Por favor, configure seu CLIENT_ID e CLIENT_SECRET no .env"
    return f"Servico de autenticacao '{service}' nao suportado ainda."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: network_skill.py [curl|oauth] [args...]")
        sys.exit(1)
        
    cmd = sys.argv[1].lower()
    if cmd == "curl" and len(sys.argv) >= 3:
        url = sys.argv[2]
        method = sys.argv[3] if len(sys.argv) > 3 else "GET"
        print(run_curl(url, method))
    elif cmd == "oauth" and len(sys.argv) >= 3:
        print(oauth_flow(sys.argv[2]))
