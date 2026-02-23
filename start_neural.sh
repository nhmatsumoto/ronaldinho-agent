#!/bin/bash
# Ronaldinho Neural Core Startup (Linux/macOS)
echo "⚽ Starting Ronaldinho Neural Core (Hyper-Converged)..."

# Check for .NET
if ! command -v dotnet &> /dev/null
then
    echo "❌ .NET SDK not found. Please install .NET 9+ (or newer)."
    exit 1
fi

# Allow net9.0 apps to run on newer installed runtimes (for example .NET 10).
export DOTNET_ROLL_FORWARD=Major

PROJECT_PATH="services/Ronaldinho.NeuralCore/Ronaldinho.NeuralCore.csproj"

if [ ! -f "$PROJECT_PATH" ]; then
    echo "❌ Project file not found at $PROJECT_PATH"
    exit 1
fi

# Check for configuration
ENV_PATH=".env"
IS_CONFIGURED=false

if [ -f "$ENV_PATH" ]; then
    ENV_CONTENT=$(cat "$ENV_PATH")
    # Check if we have a Telegram token AND at least one LLM key that isn't a placeholder
    if [[ $ENV_CONTENT =~ TELEGRAM_BOT_TOKEN=[a-zA-Z0-9:-]{15,} ]] && \
       ([[ $ENV_CONTENT =~ GEMINI_API_KEY=AIza[a-zA-Z0-9_-]{30,} ]] || \
        [[ $ENV_CONTENT =~ OPENAI_API_KEY=sk-[a-zA-Z0-9_-]{30,} ]] || \
        [[ $ENV_CONTENT =~ ANTHROPIC_API_KEY=sk-ant-[a-zA-Z0-9_-]{30,} ]]); then
        IS_CONFIGURED=true
    fi
fi

# Run the project
echo "🧠 Orchestrating NeuralCore..."
NEURAL_CORE_PROJECT="services/Ronaldinho.NeuralCore/Ronaldinho.NeuralCore.csproj"
BRIDGE_PROJECT="services/Ronaldinho.Bridge/Ronaldinho.Bridge.csproj"

# Start NeuralCore in background
dotnet run --project "$NEURAL_CORE_PROJECT" &
NEURAL_PID=$!

if [ "$IS_CONFIGURED" = true ]; then
    echo "✅ Configuration detected. Launching Telegram Bridge..."
    dotnet run --project "$BRIDGE_PROJECT" &
    BRIDGE_PID=$!
    echo "⚽ Ronaldinho is ready and listening. (PIDs: $NEURAL_PID, $BRIDGE_PID)"
else
    echo "⚠️ Ronaldinho is UNCONFIGURED."
    echo "🚀 Launching Governance Interface for initial setup..."
    
    # Launch ConfigUI
    bash "./dev_scripts/start_ui.sh" &
    UI_PID=$!
    
    # Give it a moment and open browser
    sleep 5
    if command -v open &> /dev/null; then
        open "http://localhost:5173"
    elif command -v xdg-open &> /dev/null; then
        xdg-open "http://localhost:5173"
    fi
    
    echo "📌 Please complete the setup in your browser to start using Ronaldinho."
fi

# Trap to kill background processes on exit
trap "kill $NEURAL_PID $BRIDGE_PID $UI_PID 2>/dev/null" EXIT
wait
