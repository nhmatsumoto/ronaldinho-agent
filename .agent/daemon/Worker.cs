using System.Diagnostics;
using System.Text.RegularExpressions;

namespace Ronaldinho.Daemon;

public class Worker : BackgroundService
{
    private readonly ILogger<Worker> _logger;
    private readonly string _workspaceRoot = "/workspace";
    private readonly string _missionStorePath = "/workspace/.agent/MISSION_STORE.toon";
    private readonly string _securityPolicyPath = "/workspace/.agent/SECURITY_POLICY.toon";
    private readonly FileSystemWatcher _watcher;
    private readonly Optimizer _optimizer;

    public Worker(ILogger<Worker> logger)
    {
        _logger = logger;
        _optimizer = new Optimizer(logger);
        
        // Configura o Watcher para monitorar mudanças no MISSION_STORE
        _watcher = new FileSystemWatcher("/workspace/.agent")
        {
            Filter = "MISSION_STORE.toon",
            NotifyFilter = NotifyFilters.LastWrite
        };
        _watcher.Changed += OnMissionStoreChanged;
    }

    private void OnMissionStoreChanged(object sender, FileSystemEventArgs e)
    {
        _logger.LogInformation("MISSION_STORE alterado. Reavaliando missões...");
        // Gatilho para processamento imediato
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("--- Ronaldinho-Daemon .NET Iniciado (L5) ---");
        _watcher.EnableRaisingEvents = true;

        while (!stoppingToken.IsCancellationRequested)
        {
            try 
            {
                await _optimizer.CheckPerformanceGapsAsync();
                await ProcessMissionsAsync(stoppingToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Erro no loop principal do daemon");
            }

            await Task.Delay(TimeSpan.FromSeconds(30), stoppingToken);
        }
    }

    private async Task ProcessMissionsAsync(CancellationToken ct)
    {
        if (!File.Exists(_missionStorePath)) return;

        var content = await File.ReadAllTextAsync(_missionStorePath, ct);
        var missions = ParseMissions(content);

        var activeMissions = missions.Where(m => m.Status == "EM_PROGRESSO" || m.Status == "EM_PLANEJAMENTO");
        
        // MULTITASKING: Processa missões em paralelo usando TPL
        var tasks = activeMissions.Select(m => Task.Run(() => ExecuteMissionAsync(m, ct), ct));
        await Task.WhenAll(tasks);
    }

    private async Task ExecuteMissionAsync(Mission m, CancellationToken ct)
    {
        _logger.LogInformation("Executando Missão [{id}]: {name}", m.Id, m.Name);
        
        // Exemplo de uso da Toolbox: Busca rápida de erros críticos
        var logs = Ronaldinho.Toolbox.SearchTools.FindLinesWithPattern(_workspaceRoot, "CRITICAL");
        foreach(var log in logs) {
            _logger.LogWarning("Trigger Detectado pela Toolbox: {log}", log);
        }
        
        await Task.Delay(2000, ct); // Simula trabalho persistente
    }

    private List<Mission> ParseMissions(string content)
    {
        var missions = new List<Mission>();
        var lines = content.Split('\n');
        
        // Regex simples para extrair da tabela markdown
        foreach (var line in lines)
        {
            if (line.Contains("| M-"))
            {
                var parts = line.Split('|').Select(p => p.Trim()).ToArray();
                if (parts.Length >= 6)
                {
                    missions.Add(new Mission { 
                        Id = parts[1], 
                        Name = parts[2], 
                        Status = parts[3] 
                    });
                }
            }
        }
        return missions;
    }

    public override void Dispose()
    {
        _watcher.Dispose();
        base.Dispose();
    }
}

public class Mission
{
    public string Id { get; set; } = "";
    public string Name { get; set; } = "";
    public string Status { get; set; } = "";
}
