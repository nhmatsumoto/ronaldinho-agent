using System.ComponentModel;
using System.Text.Json;
using Microsoft.SemanticKernel;

namespace Ronaldinho.NeuralCore.Services.SuperToolbox;

public class LogAnalyzerSkill
{
    private readonly string _logsDirectory;

    public LogAnalyzerSkill(string rootPath)
    {
        _logsDirectory = Path.Combine(rootPath, "logs", "runs");
    }

    [KernelFunction("analyze_recent_governance_logs")]
    [Description("Reads and summarizes the most recent JSONL governance logs execution events. Use this to understand what Ronaldinho recently did or to verify compliance.")]
    public async Task<string> AnalyzeRecentLogsAsync(
        [Description("The number of recent days to look back for logs")] int daysBack = 1)
    {
        if (!Directory.Exists(_logsDirectory))
            return "Nenhum diretório de log de governança encontrado.";

        var recentLogs = new List<string>();
        var earliestDate = DateTime.Now.Date.AddDays(-daysBack);

        var dateDirectories = Directory.GetDirectories(_logsDirectory);

        foreach (var dir in dateDirectories)
        {
            var dirName = new DirectoryInfo(dir).Name;
            if (DateTime.TryParse(dirName, out var date) && date >= earliestDate)
            {
                var files = Directory.GetFiles(dir, "*.jsonl");
                foreach (var file in files)
                {
                    try
                    {
                        var lines = await File.ReadAllLinesAsync(file);
                        recentLogs.AddRange(lines);
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"[LogAnalyzer] Failed to read log file {file}: {ex.Message}");
                    }
                }
            }
        }

        if (recentLogs.Count == 0)
            return $"Nenhum log de governança encontrado nos últimos {daysBack} dias.";

        // Returns raw JSONL strings; the LLM handles summarization
        return string.Join(Environment.NewLine, recentLogs);
    }
}
