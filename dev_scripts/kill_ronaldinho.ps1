# Kill Ronaldinho Processes
echo "🛑 Parando Ronaldinho.Bridge e Python Runner..."

try {
    taskkill /F /IM Ronaldinho.Bridge.exe /T 2>$null
    taskkill /F /IM python.exe /T 2>$null
    echo "✅ Processos finalizados com sucesso."
} catch {
    echo "⚠️ Nenhum processo ativo encontrado ou erro ao finalizar."
}
