using Microsoft.Extensions.Logging;

namespace Ronaldinho.Daemon;

public class Optimizer
{
    private readonly ILogger<Optimizer> _logger;
    private readonly string _logPath;
    private readonly string _missionStorePath;

    public Optimizer(ILogger<Optimizer> logger)
    {
        _logger = logger;
        string root = Directory.Exists("/workspace") ? "/workspace" : Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "../../../../../"));
        _logPath = Path.Combine(root, ".agent/PERFORMANCE_LOG.toon");
        _missionStorePath = Path.Combine(root, ".agent/MISSION_STORE.toon");
    }

    public async Task CheckPerformanceGapsAsync()
    {
        if (!File.Exists(_logPath)) return;

        var lines = await File.ReadAllLinesAsync(_logPath);
        // Lógica simplificada: se uma operação leva mais de 500ms, sugere otimização
        foreach (var rawLine in lines)
        {
            var line = Ronaldinho.Toolbox.SecurityGuard.Sanitize(rawLine);
            if (line.Contains("ms |"))
            {
                var parts = line.Split('|');
                if (parts.Length > 3 && int.TryParse(parts[3].Replace("ms", "").Trim(), out int ms) && ms > 500)
                {
                    _logger.LogWarning("Gargalo detectado: {op} levou {ms}ms. Iniciando Missão de Auto-Otimização.", parts[2].Trim(), ms);
                    await CreateOptimizationMissionAsync(parts[2].Trim());
                }
            }
        }
    }

    private async Task CreateOptimizationMissionAsync(string operation)
    {
        string apiKey = Environment.GetEnvironmentVariable("GEMINI_API_KEY") ?? "";
        if (!string.IsNullOrEmpty(apiKey))
        {
            var gemini = new Ronaldinho.Toolbox.GeminiClient(apiKey);
            _logger.LogInformation("Solicitando sugestão de otimização ao Gemini para {op}...", operation);
            // Aqui poderíamos chamar o Gemini para pré-analisar o código
        }

        var missionEntry = $"| M-OPT-{Guid.NewGuid().ToString()[..4]} | Otimizar {operation} | EM_PLANEJAMENTO | ALTA | Refatorar algoritmo em Ronaldinho.Toolbox via Gemini Intelligence |\n";
        await File.AppendAllTextAsync(_missionStorePath, missionEntry);
    }
}
