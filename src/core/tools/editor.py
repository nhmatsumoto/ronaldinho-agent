import os

class EditorTool:
    def __init__(self, root_path: str):
        self.root_path = root_path

    def read_file(self, file_path: str) -> str:
        """Reads the content of a file."""
        full_path = self._get_full_path(file_path)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def write_file(self, file_path: str, content: str) -> str:
        """Writes content to a file, overwriting existing content."""
        full_path = self._get_full_path(file_path)
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    def list_files(self, directory: str = ".") -> str:
        """Lists files in a directory."""
        full_path = self._get_full_path(directory)
        try:
            files = os.listdir(full_path)
            return "\n".join(files)
        except Exception as e:
            return f"Error listing files: {str(e)}"

    def _get_full_path(self, path: str) -> str:
        if os.path.isabs(path):
            return path
        return os.path.join(self.root_path, path)
