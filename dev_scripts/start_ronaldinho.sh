#!/bin/bash
# Ronaldinho Startup Script (Linux/macOS)
echo "🚀 Initializing Ronaldinho System..."

# Check for .NET
if ! command -v dotnet &> /dev/null
then
    echo "❌ .NET SDK not found. Please install .NET 9."
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null
then
    echo "❌ Python 3 not found. Please install Python 3."
    exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ROOT_DIR="$SCRIPT_DIR/.."
ENV_PATH="$ROOT_DIR/.env"
IS_CONFIGURED=false

if [ -f "$ENV_PATH" ]; then
    ENV_CONTENT=$(cat "$ENV_PATH")
    if [[ $ENV_CONTENT =~ TELEGRAM_BOT_TOKEN=[a-zA-Z0-9:-]{15,} ]] && \
       ([[ $ENV_CONTENT =~ GEMINI_API_KEY=AIza[a-zA-Z0-9_-]{30,} ]] || \
        [[ $ENV_CONTENT =~ OPENAI_API_KEY=sk-[a-zA-Z0-9_-]{30,} ]] || \
        [[ $ENV_CONTENT =~ ANTHROPIC_API_KEY=sk-ant-[a-zA-Z0-9_-]{30,} ]]); then
        IS_CONFIGURED=true
    fi
fi

echo "🧠 Orchestrating NeuralCore..."

# Launch start_neural.sh from root
bash "$ROOT_DIR/start_neural.sh"
