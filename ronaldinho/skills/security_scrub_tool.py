import sys
import re
import json

PII_PATTERNS = {
    "email": r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
    "credit_card": r'\b(?:\d[ -]*?){13,16}\b',
    "api_key": r'(?:key|token|auth|pwd|password|secret)[-_\s]*[:=][-_\s]*([a-zA-Z0-9]{16,})'
}

def scrub_content(content):
    scrubbed = content
    for label, pattern in PII_PATTERNS.items():
        scrubbed = re.sub(pattern, f"[REDACTED_{label.upper()}]", scrubbed)
    return scrubbed

def main():
    if len(sys.argv) < 2:
        content = sys.stdin.read()
    else:
        content = sys.argv[1]
        
    result = scrub_content(content)
    print(result)

if __name__ == "__main__":
    main()
