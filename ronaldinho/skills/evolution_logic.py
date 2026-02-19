import re

def get_heuristic_tool_content(text):
    text = text.lower()
    
    # 1. HTML generation template
    if "index.html" in text or "arquivo html" in text:
        content = "<html><body><h1>Gerado pelo Ronaldinho</h1><p>Missão concluída!</p></body></html>"
        return f"with open('index.html', 'w', encoding='utf-8') as f: f.write('{content}')\nprint('Arquivo index.html criado!')"

    # 2. Basic Math template (if not already handled by regex)
    if "calcule" in text or "resultado" in text:
        # Extract numbers and operators
        math_match = re.search(r"([\d\+\-\*\/\(\)\. ]+)", text)
        if math_match:
             return f"print({math_match.group(1).strip()})"

    # 3. Default empty tool
    return f"# Ferramenta gerada para: {text}\nprint('Ronaldinho processou seu pedido.')"
