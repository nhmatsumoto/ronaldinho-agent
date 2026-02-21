using System.Text.Json;

namespace Ronaldinho.NeuralCore.Core.Memory;

public class MemoryEntry
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public required string SessionId { get; set; }
    public required string Role { get; set; } // "user" or "assistant"
    public required string Content { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
}

public class MemoryStore
{
    private readonly string _storageDir;
    private readonly TemporalDecayEngine _decayEngine;

    public MemoryStore(string rootPath)
    {
        _storageDir = Path.Combine(rootPath, "ronaldinho", "memory");
        if (!Directory.Exists(_storageDir))
        {
            Directory.CreateDirectory(_storageDir);
        }
        
        _decayEngine = new TemporalDecayEngine();
    }

    public async Task SaveMemoryAsync(string sessionId, string role, string content)
    {
        var entry = new MemoryEntry
        {
            SessionId = sessionId,
            Role = role,
            Content = content
        };

        var filePath = Path.Combine(_storageDir, $"{sessionId}.jsonl");
        var json = JsonSerializer.Serialize(entry);
        
        // Append to the session's memory log
        await File.AppendAllTextAsync(filePath, json + Environment.NewLine);
    }

    public async Task<List<MemoryEntry>> RetrieveRelevantContextAsync(string sessionId, int maxTokens = 2000)
    {
        var filePath = Path.Combine(_storageDir, $"{sessionId}.jsonl");
        if (!File.Exists(filePath))
            return new List<MemoryEntry>();

        var lines = await File.ReadAllLinesAsync(filePath);
        var entries = lines
            .Where(l => !string.IsNullOrWhiteSpace(l))
            .Select(l => JsonSerializer.Deserialize<MemoryEntry>(l)!) // Explicitly tell compiler it won't be null after filter
            .Where(e => e != null)
            .ToList();

        // Pass to TemporalDecayEngine to sort and filter by relevance/time
        return _decayEngine.ApplyDecay(entries, maxTokens);
    }
}
