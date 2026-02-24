import subprocess
import os
import json

class DevToolkit:
    def __init__(self, root_path: str):
        self.root_path = root_path

    def run_command(self, cmd: list) -> str:
        try:
            result = subprocess.run(
                cmd,
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\nCode: {result.returncode}"
        except Exception as e:
            return f"Error: {str(e)}"

    def check_lint(self, path: str) -> str:
        """Executa flake8 no caminho especificado."""
        # Tenta usar flake8 se disponível
        return self.run_command(["flake8", path])

    def format_code(self, path: str) -> str:
        """Executa black no caminho especificado."""
        return self.run_command(["black", path])

    def get_git_status(self) -> str:
        """Retorna o status atual do repositório git."""
        return self.run_command(["git", "status"])

    def git_commit(self, message: str) -> str:
        """Realiza git add . e git commit."""
        self.run_command(["git", "add", "."])
        return self.run_command(["git", "commit", "-m", message])

    def docker_ps(self) -> str:
        """Lista containers docker ativos."""
        return self.run_command(["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"])

    def docker_logs(self, container_name: str) -> str:
        """Pega os últimos logs de um container."""
        return self.run_command(["docker", "logs", "--tail", "50", container_name])

    def run_python_sandbox(self, code: str) -> str:
        """Executa código Python em um container isolado para testes e auto-aprimoramento."""
        import uuid
        temp_file = f"/tmp/sandbox_{uuid.uuid4().hex}.py"
        try:
            with open(temp_file, "w") as f:
                f.write(code)
            
            # Executa usando docker run --rm
            # Mapeia o arquivo temporário para dentro do container
            cmd = [
                "docker", "run", "--rm",
                "-v", f"{temp_file}:/app/script.py",
                "python:3.11-slim",
                "python", "/app/script.py"
            ]
            return self.run_command(cmd)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
