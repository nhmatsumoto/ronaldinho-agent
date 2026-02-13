using System.Diagnostics;

namespace Ronaldinho.Toolbox;

public static class PerformanceMonitor
{
    private static readonly string _logPath = "/workspace/.agent/PERFORMANCE_LOG.toon";

    public static async Task<T> MeasureAsync<T>(string operationName, Func<Task<T>> operation)
    {
        var sw = Stopwatch.StartNew();
        try
        {
            return await operation();
        }
        finally
        {
            sw.Stop();
            await LogPerformanceAsync(operationName, sw.ElapsedMilliseconds);
        }
    }

    private static async Task LogPerformanceAsync(string operationName, long elapsedMs)
    {
        var sanitizedOp = SecurityGuard.Sanitize(operationName);
        var entry = $"| {DateTime.UtcNow:yyyy-MM-dd HH:mm:ss} | {sanitizedOp} | {elapsedMs}ms |";
        
        // Simples append no log toon
        if (!File.Exists(_logPath))
        {
            await File.WriteAllTextAsync(_logPath, "# PERFORMANCE LOG (TOON)\n\n| Timestamp | Operação | Latência |\n| :--- | :--- | :--- |\n");
        }
        
        await File.AppendAllTextAsync(_logPath, entry + "\n");
    }
}
