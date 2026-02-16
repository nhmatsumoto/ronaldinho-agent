using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Hosting;
using Ronaldinho.Toolbox;

namespace Ronaldinho.Daemon;

public class Worker : BackgroundService
{
    private readonly ILogger<Worker> _logger;
    private readonly string _workspaceRoot; // Removed direct initialization
    private readonly string _missionStorePath;
    private readonly FileSystemWatcher _watcher;
    private readonly Optimizer _optimizer;
    private readonly SemaphoreSlim _fileLock = new SemaphoreSlim(1, 1);
    private DateTime _lastWatchTrigger = DateTime.MinValue;

    public Worker(ILogger<Worker> logger, ILogger<Optimizer> optimizerLogger)
    {
        _logger = logger;
        _workspaceRoot = GetWorkspaceRoot();
        _optimizer = new Optimizer(optimizerLogger, _workspaceRoot);
        
        _missionStorePath = Path.Combine(_workspaceRoot, ".agent/MISSION_STORE.toon");
        string agentPath = Path.Combine(_workspaceRoot, ".agent");
        
        _logger.LogInformation("--- Ronaldinho Runtime Diagnostics ---");
        _logger.LogInformation("Base Directory: {base}", AppDomain.CurrentDomain.BaseDirectory);
        _logger.LogInformation("Workspace Root: {root}", _workspaceRoot);
        _logger.LogInformation("Mission Store: {path}", _missionStorePath);

        if (!Directory.Exists(agentPath)) {
            _logger.LogError("Diretório .agent NÃO ENCONTRADO em: {path}", agentPath);
        }

        _watcher = new FileSystemWatcher(agentPath) 
        {
            Filter = "MISSION_STORE.toon",
            NotifyFilter = NotifyFilters.LastWrite
        };
        _watcher.Changed += OnMissionStoreChanged;
    }

    private string GetWorkspaceRoot()
    {
        if (Directory.Exists("/workspace")) return "/workspace";
        
        var current = AppDomain.CurrentDomain.BaseDirectory;
        while (!string.IsNullOrEmpty(current))
        {
            if (Directory.Exists(Path.Combine(current, ".agent"))) return current;
            var parent = Path.GetDirectoryName(current);
            if (parent == null || parent == current) break;
            current = parent;
        }
        return AppDomain.CurrentDomain.BaseDirectory;
    }

    private void OnMissionStoreChanged(object sender, FileSystemEventArgs e)
    {
        if ((DateTime.Now - _lastWatchTrigger).TotalSeconds < 2) return;
        _lastWatchTrigger = DateTime.Now;
        _logger.LogInformation("MISSION_STORE alterado. Reavaliando missões em breve...");
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
        try 
        {
            if (!File.Exists(_missionStorePath)) 
            {
                _logger.LogWarning("Mission Store não encontrado em: {path}", _missionStorePath);
                return;
            }

            string content;
            await _fileLock.WaitAsync(ct);
            try {
                content = await File.ReadAllTextAsync(_missionStorePath, ct);
            } finally {
                _fileLock.Release();
            }

            var missions = ParseMissions(content);
            var activeMissions = missions.Where(m => m.Status == "EM_PROGRESSO" || m.Status == "EM_PLANEJAMENTO");
            
            // Sequential to avoid file racing during status updates if they finish fast
            foreach (var m in activeMissions) {
                await ExecuteMissionAsync(m, ct);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Erro ao processar missões em {path}", _missionStorePath);
        }
    }

    private async Task ExecuteMissionAsync(Mission m, CancellationToken ct)
    {
        try 
        {
            _logger.LogInformation("Executando Missão [{id}]: {name}", m.Id, m.Name);
            
            // Simulação de trabalho
            await Task.Delay(5000, ct);

            // Atualizar status para CONCLUIDO
            await UpdateMissionStatusAsync(m.Id, "CONCLUIDO", ct);
            _logger.LogInformation("Missão [{id}] CONCLUÍDA com sucesso.", m.Id);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Erro ao executar missão {id}", m.Id);
            await UpdateMissionStatusAsync(m.Id, "FALHA", ct);
        }
    }

    private async Task UpdateMissionStatusAsync(string id, string newStatus, CancellationToken ct)
    {
        await _fileLock.WaitAsync(ct);
        try 
        {
            var content = await File.ReadAllTextAsync(_missionStorePath, ct);
            var lines = content.Split('\n').ToList();
            for (int i = 0; i < lines.Count; i++)
            {
                if (lines[i].Contains($"| {id} |"))
                {
                    var parts = lines[i].Split('|').Select(p => p.Trim()).ToArray();
                    if (parts.Length >= 6)
                    {
                        parts[3] = newStatus;
                        lines[i] = $"| {string.Join(" | ", parts.Skip(1).Take(parts.Length - 2))} |";
                    }
                }
            }
            await File.WriteAllLinesAsync(_missionStorePath, lines, ct);
        }
        finally
        {
            _fileLock.Release();
        }
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
