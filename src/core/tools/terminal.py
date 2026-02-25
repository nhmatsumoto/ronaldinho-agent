import subprocess
import os

class TerminalTool:
    def __init__(self, root_path: str):
        self.root_path = root_path

    def execute(self, command: str) -> str:
        """Executes a shell command and returns structured feedback."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=60 # Increased timeout for complex builds
            )
            
            output = []
            if result.stdout:
                output.append(f"--- STDOUT ---\n{result.stdout}")
            if result.stderr:
                output.append(f"--- STDERR ---\n{result.stderr}")
            
            status = f"--- EXIT CODE: {result.returncode} ---"
            output.append(status)
            
            return "\n".join(output) if output else "[Command completed with no output]"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 60 seconds."
        except Exception as e:
            return f"Error executing command: {str(e)}"
